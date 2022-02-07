#
# Copyright 2022 The Applied Research Laboratory for Intelligence and Security (ARLIS)
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import distill
import testing_utils

def test_find_meta_values():
    data = testing_utils.setup("./data/sample_data.json", "integer")
    sorted_dict = data[1]
    clientTimes = distill.find_meta_values('clientTime', sorted_dict)
    assert len(clientTimes) == 13
    assert 1623691890656 in clientTimes
    assert 1623691891459 in clientTimes
    assert 1623691892888 in clientTimes
    assert 1623691904212 in clientTimes
    assert 1623691904488 in clientTimes
    assert 1623691904724 in clientTimes
    assert 1623691904923 in clientTimes
    assert 1623691905176 in clientTimes
    assert 1623691905955 in clientTimes
    assert 1623691907135 in clientTimes
    assert 1623691907136 in clientTimes
    assert 1623691907302 in clientTimes
    assert 1623691909728 in clientTimes


# TODO: Possible bug when unique=False
#def test_find_meta_values_2():
#    data = testing_utils.setup("./data/sample_data.json", "integer")
#    sorted_dict = data[1]
#    clientTimes = distill.find_meta_values('clientTime', sorted_dict, unique=False)
#    assert len(clientTimes) == 18
