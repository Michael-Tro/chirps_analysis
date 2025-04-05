FROM ghcr.io/astral-sh/uv:python3.12-bookworm

ARG PROJECT_NAME

# Set up workdir
RUN mkdir /$PROJECT_NAME
WORKDIR /$PROJECT_NAME

COPY pyproject.toml ./pyproject.toml

# Install JupyterLab and other dependencies using pip
RUN uv pip install --system -r pyproject.toml

# # Create a non-root user for security
# RUN useradd -m jupyteruser && \
#     chown -R jupyteruser:jupyteruser /mnt

# # Switch to the non-root user
# USER jupyteruser

# # Set the working directory for the user
# WORKDIR /home/jupyteruser

# Expose the JupyterLab port
EXPOSE 8888

# Set the command to start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
