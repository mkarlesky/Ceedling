#!/bin/bash
# Usage: run.sh <args...>  -- runs this checkout's Ceedling in proj/
cd "$(dirname "$0")/proj"
BUNDLE_GEMFILE=/home/user/Ceedling/Gemfile bundle exec ruby /home/user/Ceedling/bin/ceedling "$@"
