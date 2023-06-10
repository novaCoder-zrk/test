#!/bin/bash

cd backend
flask run &
cd ..

cd frontend
npm run dev &

