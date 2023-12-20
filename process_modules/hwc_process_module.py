#********************************************************************************
#  Copyright (c) 2023 Datasance Teknoloji A.S.
#
#  This program and the accompanying materials are made available under the
#  terms of the Eclipse Public License v. 2.0 which is available at
#  http://www.eclipse.org/legal/epl-2.0
#
#  SPDX-License-Identifier: EPL-2.0
#********************************************************************************

"""
HWC - Hardware Capabilities
Process module and a wrapper around common Linux commands to check hardware information:
- lscpu
- lspci
- lshw
- lsusb
- parsed /proc/cpuinfo file
"""

import json
from subprocess import check_output, CalledProcessError, STDOUT

from constants import *
from process_modules.process_modules_templates import RESTRequestProcessModule
from exception import HALException


class HWCRESTRequestProcessModule(RESTRequestProcessModule):

    def process_get_request(self, http_handler):
        response = None
        if HAL_HWC_GET_LSCPU_INFO_URL in http_handler.path:
            response = self.get_lscpu_info()
        elif HAL_HWC_GET_LSPCI_INFO_URL in http_handler.path:
            response = self.get_lspci_info()
        elif HAL_HWC_GET_CPU_INFO_URL in http_handler.path:
            response = self.get_proc_cpu_info_info()
        elif HAL_HWC_GET_LSHW_INFO_URL in http_handler.path:
            response = self.get_lshw_info()
        elif HAL_HWC_GET_LSUSB_INFO_URL in http_handler.path:
            response = self.get_lsusb_info()
        else:
            message = 'This url is not supported: {}'.format(http_handler.path)
            raise HALException(message=message)
        if response is not None:
            http_handler.send_ok_response(json.dumps(response))
        return

    @staticmethod
    def _run_cmd(cmd):
        try:
            return check_output(cmd, stderr=STDOUT).decode()
        except CalledProcessError as cmd_e:
            raise HALException(cmd_e.returncode, cmd_e.output.decode())
        except Exception as e:
            raise HALException(message=str(e))

    @staticmethod
    def get_lsusb_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSUSB_CMD)
        processed_result = []
        lines = result.splitlines()
        for line in lines:
            tokens = line.split()
            if len(tokens) >= 6:
                id_tokens = tokens[5].split(':')
                element = {
                    HAL_LSUSB_BUS_NUMBER_PROPERTY_NAME: tokens[1],
                    HAL_LSUSB_DEVICE_NUMBER_PROPERTY_NAME: tokens[3][:-1],
                    HAL_LSUSB_MANUFACTURE_ID_PROPERTY_NAME: id_tokens[0],
                    HAL_LSUSB_DEVICE_ID_PROPERTY_NAME: id_tokens[1]
                }
                if len(tokens) > 6:
                    element[HAL_LSUSB_MANUFACTURE_AND_DEVICE_NAME_PROPERTY_NAME] = ' '.join(tokens[6:])
                processed_result.append(element)
        return processed_result

    @staticmethod
    def get_lscpu_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSCPU_CMD)
        processed_result = {}
        lines = result.splitlines()
        for line in lines:
            tokens = line.split(':')
            if len(tokens) >= 2:
                property_name = tokens[0].replace(' ', '_').replace('-', '_')\
                    .replace('(', '').replace(')', '').lower()
                processed_result[property_name] = tokens[1].strip()
        return processed_result

    @staticmethod
    def get_proc_cpu_info_info():
        result = HWCRESTRequestProcessModule._run_cmd(CPU_INFO_CMD)
        processed_result = []
        result = result.replace('\t', '')
        tokens = result.strip('\t').split('processor')
        for token in tokens:
            if len(token) != 0:
                processor_info = {}
                properties = token.splitlines()
                for property_line in properties:
                    if len(property_line) != 0:
                        property_tokens = property_line.split(':')
                        if len(property_tokens) == 2:
                            if len(property_tokens[0]) == 0:
                                property_name = 'processor_number'
                            else:
                                property_name = property_tokens[0].replace(' ', '_')
                            processor_info[property_name] = property_tokens[1].strip()
                processed_result.append(processor_info)
        return processed_result

    @staticmethod
    def get_lspci_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSPCI_CMD)
        processed_result = []
        lines = result.splitlines()
        for line in lines:
            tokens = line.split('"')
            if len(tokens) >= 6:
                element = {}
                numbers = tokens[0].split(':')
                if len(numbers) == 2:
                    element[HAL_LSPCI_BUS_NUMBER_PROPERTY_NAME] = numbers[0]
                    sub_numbers = numbers[1].split('.')
                    if len(sub_numbers) == 2:
                        element[HAL_LSPCI_DEVICE_NUMBER_PROPERTY_NAME] = sub_numbers[0]
                        element[HAL_LSPCI_FUNCTION_NUMBER_PROPERTY_NAME] = sub_numbers[1]
                class_props = tokens[1].split('[')
                if len(class_props) == 2:
                    element[HAL_LSPCI_DEVICE_CLASS_PROPERTY_NAME] = class_props[0]
                    element[HAL_LSPCI_DEVICE_CLASS_ID_PROPERTY_NAME] = class_props[1][:-1]
                vendor_props = tokens[3].split('[')
                if len(vendor_props) == 2:
                    element[HAL_LSPCI_DEVICE_VENDOR_PROPERTY_NAME] = vendor_props[0]
                    element[HAL_LSPCI_DEVICE_VENDOR_ID_PROPERTY_NAME] = vendor_props[1][:-1]
                device_props = tokens[5].split('[')
                if len(device_props) == 2:
                    element[HAL_LSPCI_DEVICE_NAME_PROPERTY_NAME] = device_props[0]
                    element[HAL_LSPCI_DEVICE_ID_PROPERTY_NAME] = device_props[1][:-1]
                element[HAL_LSPCI_REVISION_NUMBER_PROPERTY_NAME] = tokens[6][3:]
                processed_result.append(element)
        return processed_result

    @staticmethod
    def get_lshw_info():
        result = HWCRESTRequestProcessModule._run_cmd(LSHW_CMD)
        try:
            response = json.loads(result)
            return response
        except Exception as e:
            raise HALException(message='Exception parsing \'lshw -json\' cmd results to json object: {}'.format(e))
