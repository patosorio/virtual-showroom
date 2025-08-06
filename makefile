dev-backend:
	cd backend && source venv/bin/activate && fastapi dev main.py

dev-frontend:
	cd client && npm run dev

dev:
	# Run both in background
	make dev-backend & make dev-frontend