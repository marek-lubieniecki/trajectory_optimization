# Use the official Python image as base
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Install system dependencies for scientific computing and development
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        build-essential \
        cmake \
        gfortran \
        libopenblas-dev \
        liblapack-dev \
        libffi-dev \
        libssl-dev \
        pkg-config \
        curl \
        wget \
        git \
        vim \
        htop \
        tree \
        jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (handled by devcontainer features, but keeping as backup)
# RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
#     && apt-get install -y nodejs

# Set up Python environment
RUN python -m pip install --upgrade pip setuptools wheel

# Install common Python development tools
RUN pip install \
    black \
    flake8 \
    pylint \
    isort \
    pytest \
    pytest-cov \
    mypy \
    pre-commit \
    jupyter \
    ipython

# Create workspace directory
WORKDIR /workspaces/trajectory_optimization

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set up git configuration for container
RUN git config --global --add safe.directory /workspaces/trajectory_optimization

# Create directories for project structure
RUN mkdir -p backend frontend tests .devcontainer

# Set environment variables
ENV PYTHONPATH=/workspaces/trajectory_optimization
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Expose ports for development servers
EXPOSE 3000 5000 8000 8080

# Default command
CMD ["bash"]