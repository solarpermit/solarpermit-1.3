import pdb
import itertools
import units.predefined

from . import nec_support as nec
# TODO: move this
from website.views.api2 import ValidationError

def nec2014_690_7_A(directives=None, ac=None, dc=None, ground=None):
    ambient_low_f = nec.get_override_ambient_low_f(directives, 'override_ambient_low_f') or fahrenheit(-40)
    def voc_ambient(module):
        specs = nec.get_prop(module, 'specifications')
        voc = nec.get_voc_stc(specs, 'voc_stc')
        coeff = nec.get_temperature_coefficient_of_voc(specs, 'temperature_coefficient_of_voc')
        if coeff is None:
            return nec.predefined_coeff(ambient_low_f) * voc
        else:
            deltaT = nec.celsius(25) - ambient_low_f
            return voc + (coeff * deltaT)
    def recurse(component):
        voc = nec.volts(0)
        if component.tag == 'module':
            voc = voc_ambient(component)
        for child in component.iterchildcomponents():
            voc += recurse(child)
        specs = nec.get_prop(component, 'specifications')
        dc_voltage_max = nec.get_dc_voltage_max(specs, 'dc_voltage_max') or nec.volts(600)
        if voc > dc_voltage_max:
            raise ValidationError("NEC 2014 690.7(A): VOC of %s (at an ambient temperature of %s) exceeds maximum voltage of %s of the %s with id '%s'." % (voc, nec.format_as_fahrenheit(ambient_low_f), dc_voltage_max, component.tag, component.id))
        return voc
    for child in dc.iterchildren():
        recurse(child)

def nec2014_690_9(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.43: No breaker or fused_disconnect found between %s with id '%s' and the %s with id '%s'"
    for type in ('main_panel', 'sub_panel'):
        for panel in ac.iterdescendants(type):
            for inverter in filter(lambda component: component.tag == 'inverter',
                                   panel.itercomponents()):
                if not any(filter(lambda component: component.tag in ('breaker', 'fused_disconnect'),
                                  itertools.takewhile(lambda parent: parent != panel,
                                                      inverter.iterancestors()))):
                    raise ValidationError(fail_msg % (panel.tag, panel.id, inverter.tag, inverter.id))

def nec2014_690_12_dc(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.12: inverter with id '%s' has no integrated_dc_disconnect and there is no disconnect or or fused_disconnect between it and the modules connected to it."
    for inverter in filter(lambda component: component.tag == 'inverter',
                           dc.itercomponents()):
        specs = nec.get_prop(inverter, 'specifications')
        if not nec.get_integrated_dc_disconnect(specs, 'integrated_dc_disconnect'):
            for module in filter(lambda component: component.tag == 'module',
                                 inverter.itercomponents()):
                if not any(filter(lambda component: component.tag in ('disconnect', 'fused_disconnect'),
                                  itertools.takewhile(lambda parent: parent != inverter,
                                                      module.iterancestors()))):
                    raise ValidationError(fail_msg % (inverter.id))

def nec2014_690_13_D(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.13(D): More than 6 disconnects exist in the %s string."
    def is_disconnect(component):
        if component.tag == 'breaker':
            return True
        if component.tag in ('disconnect', 'fused_disconnect'):
            return not (any(filter(lambda component: component.tag == 'inverter',
                                   component.iterancestors())) and \
                        any(filter(lambda component: component.tag == 'module',
                                   component.itercomponents())))
        if component.tag == 'inverter':
            specs = nec.get_prop(component, 'specifications')
            if nec.get_integrated_dc_disconnect(specs, 'integrated_dc_disconnect'):
                return True
    for string in (ac, dc):
        if len(filter(is_disconnect, string.itercomponents())) > 6:
            raise ValidationError(fail_msg % string.tag)

def nec2014_690_43(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.43: %s with id '%s' is connected to %s but not to ground."
    for string in (ac, dc):
        for component in string.itercomponents():
            if component.tag != 'wire':
                if not any(filter(lambda node: node.tag == component.tag,
                                  ground.findcomponent(component.id))):
                    raise ValidationError(fail_msg % (component.tag, component.id, string.tag))