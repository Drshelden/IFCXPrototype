"""Spawns and reuses one Node `serve.mjs` sidecar process per model, each
running ifclite's own viewer server (@ifc-lite/viewer-core) pointed at that
model's generated IFC file. Flask's /viewer-proxy/<model>/... route is the
only thing that talks to these processes; the browser never sees their
ports directly.

Kept deliberately simple (process-per-model, no eviction/idle timeout): ECS
components are write-once (no edit/mutation API exists today), so a model's
generated model.ifc never goes stale for the lifetime of the running server,
and this app's scale (a small internal tool) doesn't call for a scheduler.
"""

import os
import socket
import subprocess
import sys
import threading
import time

import requests


class ViewerSidecarManager:
    def __init__(self, sidecar_dir):
        self.sidecar_dir = sidecar_dir
        self._entries = {}  # model_name -> {'proc': Popen, 'port': int}
        self._lock = threading.Lock()

    @staticmethod
    def _pick_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]

    @staticmethod
    def _is_alive(port, timeout=0.3):
        try:
            requests.get(f'http://127.0.0.1:{port}/', timeout=timeout)
            return True
        except requests.exceptions.RequestException:
            return False

    def get_or_start(self, model_name, ifc_path):
        """Return the port of a running sidecar serving ifc_path for
        model_name, starting one if none is running yet."""
        with self._lock:
            entry = self._entries.get(model_name)
            if entry is not None and entry['proc'].poll() is None and self._is_alive(entry['port']):
                return entry['port']

            port = self._pick_free_port()
            script_path = os.path.join(self.sidecar_dir, 'serve.mjs')
            proc = subprocess.Popen(
                [
                    'node',
                    script_path,
                    '--file', ifc_path,
                    '--port', str(port),
                    '--name', model_name,
                ],
                cwd=self.sidecar_dir,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            self._entries[model_name] = {'proc': proc, 'port': port}

        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(
                    f"viewer sidecar for '{model_name}' exited early (code {proc.returncode})"
                )
            if self._is_alive(port):
                return port
            time.sleep(0.1)

        raise RuntimeError(f"viewer sidecar for '{model_name}' did not become ready in time")

    def shutdown_all(self):
        with self._lock:
            for entry in self._entries.values():
                if entry['proc'].poll() is None:
                    entry['proc'].terminate()
            self._entries.clear()
