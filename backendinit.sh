#!/bin/bash
mkdir -p backend
cd backend

# Initialize package.json
npm init -y

# Install dependencies
npm install express sqlite3 bcrypt jsonwebtoken cors dotenv
npm install -D nodemon

# Create folder structure
mkdir -p routes middleware models config