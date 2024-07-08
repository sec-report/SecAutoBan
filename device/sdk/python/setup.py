import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name="SecAutoBan",
    version="1.2",
    author="SecReport",
    author_email="sec-report@outlook.com",
    description="SecAutoBan SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sec-report/SecAutoBan",
    packages=setuptools.find_packages(),
    install_requires = ["pycryptodome", "websocket-client"]
)