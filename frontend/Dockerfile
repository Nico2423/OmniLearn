FROM node:20-alpine

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Ensure the public API URL is set at build time so the client bundle calls the host-exposed backend
ENV NEXT_PUBLIC_API_URL=http://localhost:12001/api/v1

# Build the Next.js application
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
