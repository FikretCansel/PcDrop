from setuptools import setup, find_packages

setup(
    name="file-transfer",
    version="1.0.0",
    description="A FastAPI application for transferring files via a web interface with a tkinter GUI for directory selection",
    author="Your Name",
    author_email="your_email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "jinja2",
        "aiofiles",
        "tkinter",  # Tkinter'ı ekliyoruz
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'run-file-transfer = app:main',
        ]
    },
)
