import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
    #0.0.0.0 run on any available domain (local host, only we can access it, anyone on the network can access it)