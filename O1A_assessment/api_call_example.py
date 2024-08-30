import os
import pprint
import argparse
import requests


def parse_arguments():
    parser = argparse.ArgumentParser(description='O-1A assessment.')
    parser.add_argument('--input_resume_path', type=str, default="./examples/20240804_AndyWong_Resume.pdf", help='path to your resume')
    parser.add_argument('--url', type=str, default="http://localhost:8000/process", help='url to api service')
    args = parser.parse_args()
    return args


def call_fastapi_service(
        file_path, 
        url="http://your-remote-server-url:8000/process", 
    ):
    assert os.path.isfile(file_path)
    files = {'file': open(file_path, 'rb')}
    data={
      "filename": file_path ,
      "type" : "multipart/form-data"
    }, 
    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        output = response.json()
        print(output['result']['content'])
    else:
        print(f"Error: {response.status_code}, {response.text}")


if __name__ == "__main__":
    args = parse_arguments()
    print("Parsed Arguments:")
    for key, value in vars(args).items():
        print(f"   {key}: {value}")
    call_fastapi_service(file_path=args.input_resume_path, url=args.url)