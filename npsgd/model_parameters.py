import copy

class ValidationError(RuntimeError): pass

class ModelParameter(object):
    def __init__(self, name):
        self.name = name

    def withValue(self, value):
        """Instantiates a copy of the parameter with a value.
           It may be an idea to rethink this data model later"""

        ret = copy.copy(self)
        ret.setValue(value)
        return ret

    def asDict(self):
        return {
                "name" : self.name,
                "value": self.value
        }

    def fromDict(self, d):
        if d["name"] != self.name:
            raise ValidationError("Trying to instantiate the wrong parameter (called '%s' for '%s')",\
                    self.name, d["name"])

        return self.withValue(d["value"])

    def asMatlabCode(self):
        logging.warning("Unable to convert parameter '%s' to matlab code", self.name)
        return "%s='UNABLE TO CONVERT TO MATLAB';" % self.value

    def asHTML(self):
        return "No HTML for this parameter type"

class StringParameter(ModelParameter):
    def __init__(self, name, description="", units="", default=None):
        self.name        = name
        self.description = description
        self.units       = units
        self.default     = default 
        self.value = None
        if default != None:
            self.setValue(self.default)

    def setValue(self, value):
        self.value = str(value)

    def asMatlabCode(self):
        return "%s='%s';" % (self.name, matlabEscape(self.value))

    def asLatexRow(self):
        return "%s & %s & %s %s" % (self.name, self.description, latexEscape(self.value), latexEscape(self.units))
    
    def asHTML(self):
        if self.value == None:
            valueString = ""
        else:
            valueString = str(self.value)

        return "<tr><td><label for='%s'>%s</label></td><td><input type='text' name='%s' value='%s'/></td></tr>" %\
                (self.name, self.description, self.name, valueString)


class RangeParameter(ModelParameter):
    def __init__(self, name, description="", rangeStart=1.0, rangeEnd=10.0, step=1.0, units="", default=None):
        self.name        = name
        self.description = description
        self.rangeStart  = rangeStart
        self.rangeEnd    = rangeEnd
        self.step        = step
        self.default     = None
        self.units       = units
        self.value = None

        if default != None:
            self.setValue(self.default)

    def setValue(self, value):
        if isinstance(value, basestring):
            start, end = [float(e.strip()) for e in value.split("-")]
        else:
            start, end = map(float, value)

        self.value = (start, end)

    def asMatlabCode(self):
        start, end = self.value
        return "%sStart=%s;\n%sEnd=%s;\n%s=%s:%s:%s;" % (self.name, start, self.name, end, self.name, start, self.step, end)

    def asLatexRow(self):
        return "%s & %s & %s-%s %s" % (latexEscape(self.name), latexEscape(self.description), self.value[0], self.value[1], latexEscape(self.units))

    def asHTML(self):
        if self.value == None:
            valueString = ""
        else:
            valueString = "%s-%s" % (self.value[0], self.value[1])

        return """
                <tr class="rangeParameter">
                    <td>
                        <label for='%s'>%s</label> 
                    </td>
                    <td>
                        <input type='text' name='%s' value='%s' /> %s
                        <input type='hidden' class='rangeStart' value='%s' />
                        <input type='hidden' class='rangeEnd' value='%s' />
                        <input type='hidden' class='step' value='%s' />
                        <div class="slider"></div>
                    </td>
                </tr>
""" % (self.name, self.description, self.name, valueString, self.units, self.rangeStart, self.rangeEnd, self.step)

class FloatParameter(ModelParameter):
    def __init__(self, name, description="", rangeStart=None, rangeEnd=None, step=None, units="", default=None):
        self.name        = name
        self.description = description
        self.rangeStart  = rangeStart
        self.rangeEnd    = rangeEnd
        self.step        = step
        self.default     = default
        self.units = units
        self.value = None
        if default != None:
            self.setValue(self.default)

    def setValue(self, value):
        self.value = float(value)

    def asMatlabCode(self):
        return "%s=%s;" % (self.name, self.value)

    def asLatexRow(self):
        return "%s & %s & %s %s" % (latexEscape(self.name), latexEscape(self.description), self.value, latexEscape(self.units))

    def asHTML(self):
        if self.value == None:
            valueString = ""
        else:
            valueString = str(self.value)

        if self.rangeStart != None and self.rangeEnd != None and self.step != None:
            return """
                    <tr class="floatSliderParameter">
                        <td>
                            <label for='%s'>%s</label>
                        </td>
                        <td>
                            <input type='text' name='%s' value='%s'/> %s
                            <input type='hidden' class='rangeStart' value='%s' />
                            <input type='hidden' class='rangeEnd' value='%s' />
                            <input type='hidden' class='step' value='%s' />
                            <div class="slider"></div>
                        </td>
                    </tr>
    """ % (self.name, self.description, self.name, valueString, self.units, self.rangeStart, self.rangeEnd, self.step)
        else:
            return "<tr><td><label for='%s'>%s</label></td><td><input type='text' name='%s' value='%s'/> %s</td></tr>" \
                % (self.name, self.description, self.name, valueString, self.units)

class IntegerParameter(FloatParameter):
    def setValue(self, value):
        self.value = int(value)

#Some helpers
def replaceAll(replacee, replaceList):
    for find, replace in replaceList:
        replacee = replacee.replace(find, replace)

    return replacee

def matlabEscape(string):
    return string.replace("'", "\\'")\
            .replace("%", "%%")\
            .replace("\\", "\\\\")

def latexEscape(string):
    return replaceAll(string,
            [("\\",r"\textbackslash{}"),
             ("<", r"\textless{}"),
             (">", r"\textgreater{}"),
             ("~", r"\texasciitilde{}"),
             ("^", r"\testasciicircum{}"),
             ("&", r"\&"),
             ("#", r"\#"),
             ("_", r"\_"),
             ("$", r"\$"),
             ("%", r"\%"),
             ("|", r"\docbooktolatexpipe{}"),
             ("{", r"\{"),
             ("}", r"\}")])
