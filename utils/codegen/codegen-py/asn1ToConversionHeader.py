#!/usr/bin/env python3

# ==============================================================================
# MIT License
#
# Copyright (c) 2023-2025 Institute for Automotive Engineering (ika), RWTH Aachen University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

import argparse
import glob
import os
from typing import Dict, List

import jinja2
from tqdm import tqdm

from asn1CodeGenerationUtils import *


def parseCli():
    """Parses script's CLI arguments.

    Returns:
        argparse.Namespace: arguments
    """

    parser = argparse.ArgumentParser(
        description="Creates header files from ASN.1 definitions for conversion between C structs and ROS messages.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("files", type=str, nargs="+", help="ASN.1 files")
    parser.add_argument("-t", "--type", type=str, required=True, help="ASN.1 type")
    parser.add_argument("-o", "--output-dir", type=str, required=True, help="output directory")

    args = parser.parse_args()

    return args


def loadJinjaTemplates() -> Dict[str, jinja2.environment.Template]:
    """Loads the jinja templates for conversion headers.

    Templates available for types `CHOICE`, `CUSTOM`, `ENUMERATED`, `PRIMITIVE`, `SEQUENCE`, `SEQUENCE OF`.

    Returns:
        Dict[str, jinja2.environment.Template]: jinja templates
    """

    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), trim_blocks=False)
    jinja_templates = {}
    jinja_templates["BIT STRING"] = jinja_env.get_template("BIT_STRING.c.j2")
    jinja_templates["CHOICE"] = jinja_env.get_template("CHOICE.c.j2")
    jinja_templates["ENUMERATED"] = jinja_env.get_template("ENUMERATED.c.j2")
    jinja_templates["IA5STRING"] = jinja_env.get_template("IA5STRING.c.j2")
    jinja_templates["OCTECT STRING"] = jinja_env.get_template("OCTET_STRING.c.j2")
    jinja_templates["SEQUENCE"] = jinja_env.get_template("SEQUENCE.c.j2")
    jinja_templates["SEQUENCE OF"] = jinja_env.get_template("SEQUENCEOF.c.j2")

    return jinja_templates

