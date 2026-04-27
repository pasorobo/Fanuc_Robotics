from glob import glob

from setuptools import find_packages, setup

package_name = "crx10ial_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Fanuc Robotics Maintainers",
    maintainer_email="codex@openai.com",
    description="Bringup launch files for the CRX-10iA/L workcell.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "publish_mock_scene = crx10ial_bringup.mock_scene_node:main",
        ],
    },
)
