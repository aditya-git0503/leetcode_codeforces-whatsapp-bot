#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
node send_report.js
