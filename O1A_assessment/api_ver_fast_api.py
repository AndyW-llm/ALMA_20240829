import argparse
from fastapi import FastAPI, File, UploadFile, Depends
import os
import shutil
import uvicorn
from O1A_assessment.utils.uuid import create_unique_id
from O1A_assessment.inference.workflows import workflows_fn

app = FastAPI()

def parse_arguments():
    parser = argparse.ArgumentParser(description='FastAPI Server for O-1A assessment.')
    parser.add_argument('--host', type=str, default="0.0.0.0", help='Host to run the FastAPI server on')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the FastAPI server on')
    parser.add_argument('--output_dir', type=str, default="./results", help='directory path to store results')
    parser.add_argument('--workflow_version', type=str, default="default", help='which version of workflow to execute')
    return parser.parse_args()

@app.post("/process")
async def process_file(
    file: UploadFile = File(...), 
    output_dir: str = Depends(lambda: args.output_dir),
    workflow_version: str = Depends(lambda: args.workflow_version)
  ):
    # Validate output directory
    task_dir = os.path.join(output_dir, create_unique_id(), workflow_version)
    os.makedirs(task_dir, exist_ok=True)

    # Save the uploaded file
    file_path = os.path.join(task_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process the file
    print(f"File saved to: {file_path}")
    print(f"Executing: {workflow_version} workflow")
    result = workflows_fn[workflow_version](input_file_path = file_path, output_dir = task_dir)
    print(f"Finished {workflow_version} workflow")

    # Return a success message
    return {"message": "Processing complete", "file_path": file_path, "result":result}

if __name__ == "__main__":
    args = parse_arguments()
    uvicorn.run(app, host=args.host, port=args.port)
