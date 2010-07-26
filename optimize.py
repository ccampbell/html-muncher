#!/usr/bin/python

# Copyright 2010 Craig Campbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from modules.optimizer import Config, Optimizer, OptimizerSingleFile

config = Config()
config.processArgs()

multiple_runs = False
if config.multiple_runs is True:
    multiple_runs = True
elif config.single_file_mode is True:
    optimizer = OptimizerSingleFile(config)
else:
    optimizer = Optimizer(config)

if multiple_runs is True:
    for file in config.getViewFiles():
        config.single_file_path = file
        optimizer = OptimizerSingleFile(config)
        optimizer.setupFiles()
        optimizer.run()
    print "all done"
    sys.exit(2)

optimizer.setupFiles()
optimizer.run()
print "all done"
