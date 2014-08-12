import itertools
import units.predefined

from . import nec_support as nec
# TODO: move this
from website.views.api2 import ValidationError

def nec2014_690_7_A(directives=None, ac=None, dc=None, ground=None):
    ambient_low_f = nec.get_override_ambient_low_f(directives) or fahrenheit(-40)
    def voc_ambient(module):
        specs = nec.get_specifications(module)
        voc = nec.get_voc_stc(specs)
        coeff = nec.get_temperature_coefficient_of_voc(specs)
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
        specs = nec.get_specifications(component)
        dc_voltage_max = nec.get_dc_voltage_max(specs) or nec.volts(600)
        if voc > dc_voltage_max:
            raise ValidationError("NEC 2014 690.7(A): VOC of %s (at an ambient temperature of %s) exceeds maximum voltage of %s of the %s with id '%s'." % (voc, nec.format_as_fahrenheit(ambient_low_f), dc_voltage_max, component.tag, component.id))
        return voc
    for child in dc.iterchildren():
        recurse(child)

def nec2014_690_8(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.8: Current at %s with id '%s' exceeds 80% of its max_amps value."
    def recurse(component):
        current = nec.amps(0)
        for child in component.iterchildcomponents():
            current += recurse(child)
        specs = nec.get_specifications(component)
        this_current = nec.amps(0)
        if component.tag == 'module':
            this_current = nec.get_isc_stc(specs)
        elif component.tag == 'inverter':
            this_current = nec.get_ac_output_amps(specs)
        current = max(current, this_current)
        max_current = nec.get_max_amps(specs)
        if max_current is None:
            raise ValidationError("NEC 2014 690.8: No max_amps defined for %s with id '%s'." % (component.tag, component.id))
        if (current > (.8 * max_current)):
            raise ValidationError(fail_msg % (component.tag, component.id))
        return current
    for tree in (ac, dc):
        for child in tree.iterchildren():
            recurse(child)

def nec2014_690_6_1(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.6: AC module with id of '%s' is downstream of an inverter."
    for module in ac.iterdescendants('module'):
        if module.iterancestors('inverter'):
            raise ValidationError(fail_msg % module.id)

def nec2014_690_6_2(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.6: AC module with id of '%s' must not also appear in the DC tree."
    for module in ac.iterdescendants('module'):
        if dc.findcomponent(module.id):
            raise ValidationError(fail_msg % module.id)

def nec2014_690_6_3(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.6: AC module with id of '%s' must have both output_ac_voltage and output_ac_amps specified."
    for module in ac.iterdescendants('module'):
        specs = nec.get_specifications(module)
        voltage = nec.get_output_ac_voltage(specs)
        current = nec.get_output_ac_current(specs)
        if voltage is None or current is None:
            raise ValidationError(fail_msg % module.id)

def nec2014_690_9(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.43: No breaker or fused_disconnect found between %s with id '%s' and the %s with id '%s'"
    for type in ('main_panel', 'sub_panel'):
        for panel in ac.iterdescendants(type):
            for inverter in panel.itercomponents('inverter'):
                if not any(filter(lambda component: component.tag in ('breaker', 'fused_disconnect'),
                                  itertools.takewhile(lambda parent: parent != panel,
                                                      inverter.iterancestors()))):
                    raise ValidationError(fail_msg % (panel.tag, panel.id, inverter.tag, inverter.id))

def nec2014_690_12_dc(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.12: Inverter with id '%s' has no integrated_dc_disconnect and there is no disconnect or or fused_disconnect between it and the modules connected to it."
    for inverter in dc.itercomponents('inverter'):
        specs = nec.get_specifications(inverter)
        if not nec.get_integrated_dc_disconnect(specs):
            for module in inverter.itercomponents('module'):
                if not any(filter(lambda component: component.tag in ('disconnect', 'fused_disconnect'),
                                  itertools.takewhile(lambda parent: parent != inverter,
                                                      module.iterancestors()))):
                    raise ValidationError(fail_msg % (inverter.id))

def nec2014_690_12_ac(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.12: There is no disconnect or or fused_disconnect between inverter with id '%s' and the main_panel."
    for inverter in dc.itercomponents('inverter'):
        if not any(filter(lambda component: component.tag in ('disconnect', 'fused_disconnect'),
                          itertools.takewhile(lambda parent: parent.tag != 'main_panel',
                                              inverter.iterancestors()))):
            raise ValidationError(fail_msg % (inverter.id))

def nec2014_690_13(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.13: There are DC components between inverter with id '%s' and module with id '%s', but the inverter does not have an integrated_dc_disconnect, nor is there a disconnect or fused_disconnect between them."
    def is_disconnect(component):
        return component.tag in ('disconnect', 'fused_disconnect')
    for inverter in dc.iterdescendants('inverter'):
        for module in inverter.itercomponents('module'):
            intervening_components = itertools.takewhile(lambda c: c != module,
                                                         inverter.itercomponents())
            if len(list(intervening_components)) > 0:
                specs = nec.get_specifications(inverter)
                integrated_dc_disconnect = nec.get_integrated_dc_disconnect(specs)
                if not (integrated_dc_disconnect or any(is_disconnect, intervening_components)):
                    raise ValidationError(fail_msg % (inverter.id, panel.id))

def nec2014_690_13_D(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.13(D): More than 6 disconnects exist in the dc tree."
    def is_disconnect(component):
        if component.tag == 'breaker':
            return True
        if component.tag in ('disconnect', 'fused_disconnect'):
            return not (any(component.iterancestors('inverter')) and \
                        any(component.itercomponents('module')))
        if component.tag == 'inverter':
            specs = nec.get_specifications(component)
            if nec.get_integrated_dc_disconnect(specs):
                return True
    if len(list(filter(is_disconnect, dc.itercomponents()))) > 6:
        raise ValidationError(fail_msg)

def nec2014_690_15_1(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.15: There are no AC disconnects between inverter with id '%s' and main_panel with id '%s'."
    def is_disconnect(component):
        return component.tag in ('disconnect', 'fused_disconnect')
    for panel in ac.iterdescendants('main_panel'):
        for inverter in itertools.takewhile(lambda component: component.tag == 'inverter',
                                            panel.itercomponents()):
            intervening_components = itertools.takewhile(lambda c: c != panel,
                                                         inverter.itercomponents())
            if len(list(filter(is_disconnect, intervening_components))) == 0:
                raise ValidationError(fail_msg % (inverter.id, panel.id))

def nec2014_690_15_1(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.15: There is no breaker between inverter with id '%s' and main_panel with id '%s'."
    def is_breaker(component):
        return component.tag == 'breaker'
    for panel in ac.iterdescendants('main_panel'):
        for inverter in itertools.takewhile(lambda component: component.tag == 'inverter',
                                            panel.itercomponents()):
            intervening_components = itertools.takewhile(lambda c: c != panel,
                                                         inverter.itercomponents())
            if len(list(filter(is_breaker, intervening_components))) == 0:
                raise ValidationError(fail_msg % (inverter.id, panel.id))

def nec2014_690_15_D(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.13(D): More than 6 disconnects exist in the ac tree."
    def is_disconnect(component):
        if component.tag == 'breaker':
            if any(component.iterancestors('sub_panel')):
                return False
            return True
        if component.tag in ('disconnect', 'fused_disconnect'):
            return True
    if len(list(filter(is_disconnect, dc.itercomponents()))) > 6:
        raise ValidationError(fail_msg)

def nec2014_690_43(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.43: %s with id '%s' is connected to %s but not to ground."
    for tree in (ac, dc):
        for component in tree.itercomponents():
            if component.tag not in ('breaker', 'wire'):
                if not any(filter(lambda node: node.tag == component.tag,
                                  ground.findcomponent(component.id))):
                    raise ValidationError(fail_msg % (component.tag, component.id, tree.tag))

def nec2014_690_47_B_2(directives=None, ac=None, dc=None, ground=None):
    fail_msg = "NEC 2014 690.47(B)(2): Grounding rod with id '%s' is not made of copper."
    for rod in ground.itercomponents('grounding_rod'):
        specs = nec.get_specifications(rod)
        material = nec.get_material(specs)
        if material != "Cu":
            raise ValidationError(fail_msg % rod.id)
