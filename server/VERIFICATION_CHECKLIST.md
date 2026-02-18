# Project Reorganization - Verification Checklist

This checklist helps verify that the project reorganization has been completed successfully and the new architecture is working correctly.

## Directory Structure Verification

- [ ] `server.py` exists in project root
- [ ] `dataStores/fileBased/memoryTree.py` exists
- [ ] `dataStores/fileBased/__init__.py` exports FileBasedStore and MemoryTree
- [ ] `dataStores/mongodbBased/mongodbBased.py` exists
- [ ] `dataStores/mongodbBased/mongodbMemoryTree.py` exists  
- [ ] `dataStores/mongodbBased/__init__.py` exists
- [ ] `examples/example_usage.py` exists
- [ ] `REORGANIZATION.md` exists in project root
- [ ] `QUICK_START.md` exists in project root
- [ ] `BACKEND_INTERFACE.md` exists in project root
- [ ] `PROJECT_REORGANIZATION.md` exists in project root

**Verify with:**
```bash
ls -la server.py
ls -la dataStores/fileBased/memoryTree.py
ls -la dataStores/mongodbBased/
ls -la examples/
```

## Startup Script Verification

- [ ] `ifcxServerFileStore.py` imports and uses `server.py`
- [ ] Script offers backend selection menu (file-based, MongoDB)
- [ ] Script sets `IFC_DATA_STORE` environment variable
- [ ] Script launches `server.py` (not `app.py`)

**Test with:**
```bash
python ifcxServerFileStore.py
# Should show menu with backend options
```

## File-Based Backend Verification

- [ ] `dataStores/fileBased/fileBased.py` is unchanged
- [ ] `dataStores/fileBased/memoryTree.py` matches original functionality
- [ ] `dataStores/fileBased/__init__.py` exports both classes
- [ ] `dataStores/fileBased/data/` exists (component storage)
- [ ] Existing component files still work without issues

**Test with:**
```bash
python -c "from dataStores.fileBased import FileBasedStore, MemoryTree; print('✓ Imports work')"
```

## Core Server Verification

- [ ] `server.py` imports necessary modules
- [ ] `IFCProcessingServer` class initializes correctly
- [ ] `_initialize_backend()` handles 'fileBased' option
- [ ] `_initialize_backend()` has MongoDB stub (raises NotImplementedError)
- [ ] `create_app()` factory function exists
- [ ] Flask routes are registered correctly

**Test with:**
```bash
python -c "from server import IFCProcessingServer; s = IFCProcessingServer('fileBased'); print('✓ Server initialized')"
```

## API Endpoint Verification

Start the server and test these endpoints:

- [ ] `GET /api/status` returns data_store field
  ```bash
  curl http://localhost:5000/api/status
  # Should include: "data_store": "fileBased"
  ```

- [ ] `GET /api/stores` lists available backends
  ```bash
  curl http://localhost:5000/api/stores
  # Should list: fileBased, mongodbBased
  ```

- [ ] `GET /api/models` returns model list
- [ ] `POST /api/upload` handles file uploads
- [ ] `GET /api/components` retrieves components
- [ ] `GET /api/entityGuids` queries entities
- [ ] `GET /api/componentGuids` queries components
- [ ] `GET /api/entityTypes` lists types

**Quick test:**
```bash
# Start server
python server.py

# In another terminal, test
curl http://localhost:5000/api/status
curl http://localhost:5000/api/stores
curl http://localhost:5000/api/models
```

## Backend Selection Verification

- [ ] Environment variable `IFC_DATA_STORE` controls backend
- [ ] Default backend is 'fileBased'
- [ ] Can set via: `set IFC_DATA_STORE=fileBased`
- [ ] Server respects environment variable

**Test with:**
```bash
# Test default (file-based)
python server.py
# Check logs for "✅ Initialized file-based data store"

# Test with environment variable
set IFC_DATA_STORE=fileBased
python server.py
# Same result

# Test MongoDB stub
set IFC_DATA_STORE=mongodbBased
python server.py
# Should show "⚠️  MongoDB store initialized (stub mode)"
```

## Import Path Verification

- [ ] Can import FileBasedStore from dataStores.fileBased
  ```python
  from dataStores.fileBased import FileBasedStore
  ```

- [ ] Can import MemoryTree from dataStores.fileBased
  ```python
  from dataStores.fileBased import MemoryTree
  ```

- [ ] Can import MongoDBStore from dataStores.mongodbBased
  ```python
  from dataStores.mongodbBased import MongoDBStore
  ```

- [ ] Can import from server
  ```python
  from server import IFCProcessingServer, create_app
  ```

**Verify all imports:**
```bash
python examples/example_usage.py
# Should run without import errors
```

## Data Persistence Verification

- [ ] Existing component files still accessible
- [ ] File-based store path unchanged
- [ ] Can create new models and store components
- [ ] Components persist across server restarts

**Test with:**
```bash
# 1. Start server and upload a test file
# 2. Query the components
# 3. Stop server
# 4. Start server again
# 5. Components should still be there
```

## Documentation Verification

- [ ] `REORGANIZATION.md` explains architecture
- [ ] `QUICK_START.md` shows how to start server
- [ ] `BACKEND_INTERFACE.md` explains how to add backends
- [ ] `PROJECT_REORGANIZATION.md` summarizes changes
- [ ] All docs are readable and clear
- [ ] Examples folder has usage examples

**Verify:**
```bash
# Check files exist
ls -la REORGANIZATION.md
ls -la QUICK_START.md
ls -la BACKEND_INTERFACE.md
ls -la PROJECT_REORGANIZATION.md
```

## Backward Compatibility Verification

- [ ] API endpoints return same data structures
- [ ] Component storage location unchanged
- [ ] Query results identical to before
- [ ] All existing data accessible

**Test key scenarios:**
```bash
# 1. Upload file - should work
# 2. Query components - should work
# 3. Get models list - should work
# 4. Refresh memory - should work
```

## Flask Factory Function Verification

- [ ] `create_app()` returns Flask application
- [ ] Application has correct configuration
- [ ] Routes are registered
- [ ] Can use with test client

**Test with:**
```python
from server import create_app
app = create_app('fileBased')
client = app.test_client()
response = client.get('/api/status')
print(response.json)
```

## MongoDB Stub Verification

- [ ] MongoDBStore class exists with correct methods
- [ ] MongoDBMemoryTree class exists with correct methods
- [ ] Raises NotImplementedError appropriately
- [ ] Configuration classes exist

**Verify:**
```python
from dataStores.mongodbBased import MongoDBStore, MongoDBMemoryTree
# Should not raise ImportError

store = MongoDBStore()
# Should show "⚠️  MongoDB store initialized (stub mode)"

# These should raise NotImplementedError
try:
    store.store('test', [])
except NotImplementedError:
    print("✓ Stub methods raise NotImplementedError as expected")
```

## Server Startup Verification

### Test 1: Direct Execution
```bash
python server.py
# Should start successfully
# Should show "✅ Initialized file-based data store at: ..."
# Should show listening on 0.0.0.0:5000
```

### Test 2: Via Startup Script
```bash
python ifcxServerFileStore.py
# Should show menu
# Choose option 1
# Should start successfully
```

### Test 3: With Environment Variable
```bash
set IFC_DATA_STORE=fileBased
python server.py
# Should start successfully with file-based backend
```

### Test 4: Admin Interface
```bash
http://localhost:5000
# Should show admin page
# Should be able to upload files
```

## Performance Verification

- [ ] Server starts in < 5 seconds
- [ ] File-based queries are fast (< 100ms)
- [ ] Memory tree loads all models at startup
- [ ] No obvious performance regressions

**Test:**
```bash
# Time server startup
time python server.py
# Should be < 5 seconds

# Test query speed
curl "http://localhost:5000/api/components?models=TestModel"
# Should respond in < 1 second
```

## Error Handling Verification

- [ ] MongoDB backend on startup shows configuration stub message
- [ ] Calling unimplemented MongoDB methods shows NotImplementedError
- [ ] File-based errors still handled correctly
- [ ] Invalid backend type shows error

**Test:**
```bash
# Test unknown backend
set IFC_DATA_STORE=unknownBackend
python server.py
# Should show error about unknown backend

# Test MongoDB stub (intentionally fails)
set IFC_DATA_STORE=mongodbBased
python -c "from dataStores.mongodbBased import MongoDBStore; s = MongoDBStore(); s.store('test', [])"
# Should show: NotImplementedError...
```

## Final Verification Summary

**Complete the verification with these command sequences:**

### File-Based Backend Works
```bash
python server.py &  # Start server
sleep 2
curl http://localhost:5000/api/status
# Should show "data_store": "fileBased"
kill %1  # Stop server
```

### Startup Script Works
```bash
echo 1 | python ifcxServerFileStore.py &  # Auto-select option 1
sleep 3
curl http://localhost:5000/api/status
kill %1
```

### Imports Work
```bash
python examples/example_usage.py
# Should run without errors
```

### All Documentation Exists
```bash
ls -la *.md | grep -E "REORGANIZATION|QUICK_START|BACKEND_INTERFACE|PROJECT_REORGANIZATION"
# Should see all 4 files
```

## Completion Checklist

When all items are verified, check this final box:

- [ ] **✅ ALL VERIFICATION TESTS PASSED**
  - [ ] Directory structure correct
  - [ ] Startup script working
  - [ ] File-based backend working
  - [ ] API endpoints working
  - [ ] Backend selection working
  - [ ] MongoDB stub in place
  - [ ] Documentation complete
  - [ ] Examples provided
  - [ ] Backward compatibility preserved
  - [ ] Performance acceptable

## Next Steps After Verification

1. **Commit changes** to version control
   ```bash
   git add .
   git commit -m "Reorganize: Add pluggable backend architecture"
   ```

2. **Test with real data**
   - Upload actual IFC/JSON files
   - Query and verify results
   - Check data persistence

3. **Implement MongoDB** (when ready)
   - Use BACKEND_INTERFACE.md as guide
   - Run tests against MongoDB backend
   - Compare performance

4. **Document any custom backends** if implemented
   - Update BACKEND_INTERFACE.md with examples
   - Add to examples/
   - Test thoroughly

## Troubleshooting Failed Verification

| Issue | Solution |
|-------|----------|
| Module not found | Check imports, ensure __init__.py files exist |
| API returns 404 | Verify Routes are registered in server.py |
| MongoDB raises error immediately | This is expected (stub mode), implement backend later |
| File-based data missing | Check dataStores/fileBased/data/ directory exists |
| Port already in use | Use different port: set FLASK_PORT=5001 |
| Import circular references | Check __init__.py files for circular imports |

---

**Verification Status**: ⏳ Ready to verify  
**Expected Duration**: 15-30 minutes  
**Difficulty**: Easy to Medium

Use this checklist to ensure the reorganization is complete and working correctly!
