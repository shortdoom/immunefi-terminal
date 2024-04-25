# Check if the 'targets' directory is empty or not
if [ -z "$(ls -A targets)" ]; then
   echo "The 'targets' directory is empty. Cloning the submodule..."
   git submodule update --init --recursive
else
   echo "The 'targets' directory is not empty. The submodule has been cloned."
fi

# Create a new Python environment
python3 -m venv venv

# Activate the Python environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt