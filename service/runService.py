from app import create_app

app, socket = create_app()

if __name__ == "__main__":
    socket.run(app, host="localhost", port=5000, debug = True)
