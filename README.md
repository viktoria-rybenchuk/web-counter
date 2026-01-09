# Async Web Counter

A simple asynchronous web counter built with FastAPI. Supports in-memory and file-based storage and includes a load testing client.

---


### 2. Set Storage Type (Optional)

By default, the counter is stored in memory. You can switch to file storage if you want the counter to persist between server restarts.

Set the storage type with an environment variable:

```bash
export STORAGE_TYPE=FILE   # Use FILE to store counter in a file
# or
export STORAGE_TYPE=MEMORY # Default in-memory storage
```
### 3. Start the Server

Run the FastAPI server using **uvicorn**:

```bash
uvicorn main:app --host 127.0.0.1 --port 8080
```

### 4. Use the API

**Increment the counter:**

```bash
curl http://127.0.0.1:8081/inc
```
**Get the current counter value:**

```bash
curl http://127.0.0.1:8081/count
```
### 5. Load Testing

You can test the server with multiple concurrent requests using the load testing script:

```bash
python load_test_client.py --clients 10 --requests 1000
```
#### Command Line Arguments

- `--clients` : Specifies the **number of concurrent clients**.
- `--requests` : Specifies the **number of requests per client**.
