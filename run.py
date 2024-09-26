from app import create_app, db
from flask_migrate import Migrate

# Use the create_app function to ensure the CORS setup and other configurations are applied
app = create_app()

# Initialize migration
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)
