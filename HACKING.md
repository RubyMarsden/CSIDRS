# CSIDRS hacking guide

The CSIDRS software is designed to have a degree of flexibility - this means that the model can be changed to add methodologies. This file is written as a user guide to add a new stable isotope method - you will need to clone the repository from GitHub as this can only be done in the original python code. If you do create a new method using the CSIDRS software you must still cite the original reference of (CITE HERE) within any body of scientific literature.

#### The files that will need altering to create a new method with a new element are as follows:

- src/model/elements.py
- src/model/isotopes.py

- src/model/settings/constants.py
- src/model/settings/isotope_reference_materials.py
- src/model/settings/material_lists.py
- src/model/settings/methods_from_isotopes

- src/view/isotope_button_widget.py
- src/view/method_selection_dialog.py


#### The files that will need altering to create a new isotope method (e.g., a different subset of oxygen ratios) are as follows:

- src/model/settings/methods_from_isotopes

and in the case of new reference values for these new oxygen ratios:
- src/model/settings/isotope_reference_materials.py

As this case is covered in the method for making a totally new set of methods for a new element it will not be written about separately.

## Creating a new element method:

1. Create a new element Enum in `src/model/elements.py`
e.g.: 
    ```python
    class Element(Enum):
        OXY = "Oxygen"
        NEW_ELEMENT = "New Element"
   ```
   
2. Create the new isotope Enums in `src/model/isotopes.py`
e.g.:
    ```python
    class Isotope(Enum):
        C12 = "12C"
        NE1 = "1NE"
        NE2 = "2NE"
       
    ```
3. Create Ratio objects in `src/model/settings/methods_from_isotopes.py` where the first isotope is the numerator and the second is the denominator in the isotopic ratio. 
e.g.:
    ```python
   # Sulphur ratios
    S33_S32 = Ratio(Isotope.S33, Isotope.S32)
    S34_S32 = Ratio(Isotope.S34, Isotope.S32)
   
   # New element ratios
   NE1_NE2 = Ratio(Isotope.NE1, Isotope.NE2) 
   ```

4. Instantiate the new Method object and add it to the list of methods in `src/model/settings/methods_from_isotopes.py` e.g.:
    ```python
    three_isotopes_hydroxide_oxygen = Method([Isotope.O16, Isotope.O17, Isotope.O18, Isotope.HYD],
                                             [O17_O16, O18_O16, O16H1_O16])
    new_method = Method([Isotope.NE1, Isotope.NE2], [NE1_NE2])
   
    list_of_methods = [three_isotopes_sulphur,
                       four_isotopes_sulphur,
                       two_isotopes_hydroxide_oxygen,
                       two_isotopes_no_hydroxide_oxygen,
                       three_isotopes_hydroxide_oxygen,
                       three_isotopes_no_hydroxide_oxygen,
                       new_method
                       ]
    
    ```


5. Add the required delta notation constants into `src/model/settings/constants.py`
e.g.:
   ```python
   oxygen_isotope_reference = {
        'VSMOW': {O18_O16: 0.002005, O17_O16: 0.0003799}}
   
   new_element_isotope_reference = {
        'VNEW': {ISO_RATIO: float, ISO_RATIO_2: float}
    ```
   
6. Add the material list for the element into `src/model/settings/material_lists.py` e.g.:
   ```python
   oxygen_material_list = ['Zircon', 'Quartz']
   new_material_list = ['Mineral 1', 'Mineral 2']
   ```
7. Add the element button to `src/view/isotope_button_widget.py` e.g.:
   ```python
           layout.addWidget(self.create_O_button())
           layout.addWidget(self.create_NE_button()) 
   
       def create_O_button(self):
           o_button = QPushButton("O")
           o_button.clicked.connect(self.on_O_button_pushed)
           return o_button
   
       def on_O_button_pushed(self):
           self.element = Element.OXY
           dialog = MethodSelectionDialog(self.element)
           result = dialog.exec()
           if result:
               self.emit_methods_signal(dialog)
   
           layout.addWidget(self.create_NE_button())
   
       def create_NE_button(self):
           ne_button = QPushButton("New element")
           ne_button.clicked.connect(self.on_NE_button_pushed)
           return ne_button
   
       def on_NE_button_pushed(self):
           self.element = Element.NEW_ELEMENT
           dialog = MethodSelectionDialog(self.element)
           result = dialog.exec()
           if result:
               self.emit_methods_signal(dialog)
   ```

8. Add the possible isotopes to the method selection dialog which is called when the element button is pushed in `src/view/method_selection_dialog.py`
e.g.:
   ```python
           if self.element == Element.OXY:
   
               for isotope in three_isotopes_hydroxide_oxygen.isotopes:
                   box = QCheckBox(isotope.value)
                   box.isotope = isotope
                   box.stateChanged.connect(self.on_isotopes_changed)
   
                   lhs_box_layout.addWidget(box)
                   self.isotope_box_list.append(box)
   
               for material in oxygen_material_list:
                   box = QRadioButton(material)
                   box.material = material
                   box.toggled.connect(self.on_material_changed)
   
                   rhs_box_layout.addWidget(box)
                   self.material_box_list.append(box)
   
           elif self.element == Element.NEW_ELEMENT:
   
               for isotope in new_method.isotopes:
                   box = QCheckBox(isotope.value)
                   box.isotope = isotope
                   box.stateChanged.connect(self.on_isotopes_changed)
   
                   lhs_box_layout.addWidget(box)
                   self.isotope_box_list.append(box)
   
               for material in new_material_list:
                   box = QRadioButton(material)
                   box.material = material
                   box.toggled.connect(self.on_material_changed)
   
                   rhs_box_layout.addWidget(box)
                   self.material_box_list.append(box)
   ```