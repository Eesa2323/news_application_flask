from app import create_app

app = create_app()


if __name__ == "__main__":
    # Fire up the dev server when run directly.
    app.run(debug=True)
