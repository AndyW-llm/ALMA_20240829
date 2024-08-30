import os
from llama_index.readers.file import PyMuPDFReader 
#NOTE: require llama_index==0.10.4 or >=0.10.20

# extract_pdf_pages
def extract_pdf_pages(file_path):
    print(f"Reading PDF from {file_path}.")
    reader = PyMuPDFReader()
    pages = reader.load(file_path)
    return pages

# convert pages to text chunk
def pages_to_text_chunk(pages, prepend="", page_template="\n{text}"):
    content = "{prepend}".format(prepend=prepend)
    for _, page in enumerate(pages):
      content += page_template.format(text=page.text)
    return(content)

def pdf_to_text_ver_basic(pdf_path):
    assert os.path.isfile(pdf_path)
    pages = extract_pdf_pages(pdf_path)
    text = pages_to_text_chunk(pages)
    return text