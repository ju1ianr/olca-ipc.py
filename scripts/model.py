import glob
import yaml

from typing import List


class Model:
    def __init__(self):
        self.classes = []  # type: List[ClassType]
        self.enums = []    # type: List[EnumType]

    @staticmethod
    def load_yaml(folder):
        """
        Loads a model from a directory which contains YAML files that describe
        the model.
        :param folder: The directory that contains the YAML files (extension
            *.yaml)
        """
        m = Model()
        d = folder if folder.endswith('/') or folder.endswith('\\') else \
            folder + '/'
        files = glob.glob(d + "*.yaml")
        for file_path in files:
            with open(file_path, 'r') as f:
                yaml_model = yaml.load(f)
                if 'class' in yaml_model:
                    m.classes.append(ClassType.load_yaml(yaml_model['class']))
                if 'enum' in yaml_model:
                    m.enums.append(EnumType.load_yaml(yaml_model['enum']))
        m.enums.sort(key=lambda e: e.name)
        m._sort_classes()
        return m

    def find_class(self, name):
        if name is None:
            return None
        for t in self.types:
            if t.name == name:
                return t
        return None

    def get_super_classes(self, clazz):
        classes = []
        c = self.find_class(clazz.super_class)
        while c is not None:
            classes.append(c)
            c = self.find_class(c.super_class)
        return classes

    def _sort_classes(self):
        parent_relations = {}
        for c in self.classes:
            parent_relations[c.name] = c.super_class

        def calc_depth(class_name):
            if class_name is None:
                return 0
            super_class = parent_relations.get(class_name)
            return 1 + calc_depth(super_class)

        depths = {}
        for c in self.classes:            
            depths[c.name] = calc_depth(c.name)

        self.classes.sort(key=lambda c: c.name)
        self.classes.sort(key=lambda c: depths[c.name])


class ClassType:
    def __init__(self, name=None, super_class=None, doc=None):
        self.name = name
        self.super_class = super_class
        self.doc = doc
        self.example = None
        self.properties = []  # type: List[Property]

    @staticmethod
    def load_yaml(yaml_model):
        c = ClassType()
        c.name = yaml_model['name']
        if 'doc' in yaml_model:
            c.doc = yaml_model['doc']
        else:
            c.doc = ''
        if 'superClass' in yaml_model:
            c.super_class = yaml_model['superClass']
        if 'properties' in yaml_model:
            for prop in yaml_model['properties']:
                c.properties.append(Property.load_yaml(prop))
        if 'example' in yaml_model:
            c.example = yaml_model['example']
        return c


class Property:
    def __init__(self, name=None, field_type=None, doc=None):
        self.name = name
        self.field_type = field_type
        self.doc = doc

    @staticmethod
    def load_yaml(yaml_model):
        p = Property()
        p.name = yaml_model['name']
        p.field_type = yaml_model['type']
        if 'doc' in yaml_model:
            p.doc = yaml_model['doc']
        else:
            p.doc = ''
        return p

    @property
    def html_type_link(self):
        t = self.field_type
        if t.startswith('List['):
            end = len(t) - 1
            t = t[5:end]
        if t[0].isupper():
            return "./%s.html" % t
        else:
            return "http://www.w3.org/TR/xmlschema-2/#%s" % t


class EnumType:
    def __init__(self, name=None, doc=None):
        self.name = name
        self.doc = doc
        self.items = []

    @staticmethod
    def load_yaml(yaml_model):
        e = EnumType()
        e.name = yaml_model['name']
        if 'doc' in yaml_model:
            e.doc = yaml_model['doc']
        else:
            e.doc = ''
        if 'items' in yaml_model:
            for item in yaml_model['items']:
                e.items.append(EnumItem(item['name']))
        return e


class EnumItem:
    def __init__(self, name=None):
        self.name = name