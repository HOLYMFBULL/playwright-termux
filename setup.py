from setuptools import setup, find_packages

setup(
    name="playwright",
    version="1.62.0",
    description="Playwright Python package for Termux/Android",

    python_requires=">=3.10",

    packages=find_packages(),

    package_data={
        "playwright": [
            "py.typed",
            "driver/LICENSE",
            "driver/README.md",
            "driver/package/**",
        ],
    },

    include_package_data=True,

    install_requires=[
        "pyee>=13,<14",
        "greenlet>=3.1.1,<4.0.0",
    ],

    entry_points={
        "console_scripts": [
            "playwright=playwright.__main__:main",
        ],
    },
)
