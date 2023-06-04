import uvicorn

class App:
    ...

app = App()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5000, log_level="info")