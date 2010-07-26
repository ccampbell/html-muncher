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

from optimizer import VarFactory, Config, Optimizer, OptimizerSingleFile, Util

config = Config()
config.processArgs()

if config.single_file_mode is True:
    optimizer = OptimizerSingleFile(config)
else:
    optimizer = Optimizer(config)

optimizer.setupFiles()
optimizer.run()

print "all done"
