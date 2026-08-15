export function setupSplitter(): void {
  const splitter = document.getElementById('splitter');
  const contentSection = document.querySelector('.content-section') as HTMLElement | null;
  const leftPanel = document.querySelector('.left-panel') as HTMLElement | null;
  if (!splitter || !contentSection || !leftPanel) return;

  let resizing = false;
  splitter.addEventListener('mousedown', () => {
    resizing = true;
    splitter.classList.add('active');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  });

  document.addEventListener('mousemove', (e) => {
    if (!resizing) return;
    const rect = contentSection.getBoundingClientRect();
    const newWidth = e.clientX - rect.left;
    const minWidth = 280;
    const maxWidth = rect.width - 320;
    if (newWidth > minWidth && newWidth < maxWidth) {
      leftPanel.style.width = `${newWidth}px`;
      leftPanel.style.minWidth = 'unset';
      leftPanel.style.maxWidth = 'unset';
    }
  });

  document.addEventListener('mouseup', () => {
    if (!resizing) return;
    resizing = false;
    splitter.classList.remove('active');
    document.body.style.cursor = 'default';
    document.body.style.userSelect = 'auto';
  });
}

export function setupHorizontalSplitter(): void {
  const splitter = document.getElementById('horizontalSplitter');
  const leftPanel = document.querySelector('.left-panel') as HTMLElement | null;
  const leftUpper = document.querySelector('.left-upper') as HTMLElement | null;
  if (!splitter || !leftPanel || !leftUpper) return;

  let resizing = false;
  splitter.addEventListener('mousedown', () => {
    resizing = true;
    splitter.classList.add('active');
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
  });

  document.addEventListener('mousemove', (e) => {
    if (!resizing) return;
    const rect = leftPanel.getBoundingClientRect();
    const newHeight = e.clientY - rect.top;
    const minHeight = 180;
    const maxHeight = rect.height - 140;
    if (newHeight > minHeight && newHeight < maxHeight) {
      leftUpper.style.flex = '0 0 ' + newHeight + 'px';
    }
  });

  document.addEventListener('mouseup', () => {
    if (!resizing) return;
    resizing = false;
    splitter.classList.remove('active');
    document.body.style.cursor = 'default';
    document.body.style.userSelect = 'auto';
  });
}
