# CSIDRS hacking guide

The CSIDRS software is designed to have a degree of flexibility - this means that the model can be changed to add methodologies. This file is written as a user guide to add a new stable isotope method - you will need to clone the repository from GitHub as this can only be done in the original python code. If you do create a new method using the CSIDRS software you must still cite the original reference of (CITE HERE) within any body of scientific literature.

#### The files that will need altering to create a new method with a new element are as follows:

- src/model/elements.py
- src/model/isotopes.py
- src/model/spot.py

- src/model/settings/delta_constants.py
- src/model/settings/isotope_reference_materials.py
- src/model/settings/material_lists.py
- src/model/settings/methods_from_isotopes

- src/view/method_selection_dialog.py


#### The files that will need altering to create a new isotope method (e.g., a different subset of oxygen ratios) are as follows:

- src/model/settings/methods_from_isotopes

and in the case of new reference values for these new methods or just adding new reference values:
- src/model/settings/isotope_reference_materials.py

As this case is covered in the method for making a totally new set of methods for a new element it will not be written about separately.

## Creating a new element method:

1. Create a new element Enum in `src/model/elements.py`
e.g.: 
    ```python
   class Element(Enum):
        OXY = "Oxygen", "O"
        NEW_ELEMENT = "New Element", "Ne"
   ```
   
2. Create the new isotope Enums in `src/model/isotopes.py`. The true or false parameters indicate whether to involve these species in secondary ion calculations or not.
e.g.:
    ```python
   class Isotope(Enum):
        C12 = "12C", True
        NE1 = "1NE", False
        NE2 = "2NE", True
       
    ```
3. Add the isotopes to the isotope_by_element dictionary in `src/model/isotopes.py`
   ```python
   isotopes_by_element = {
      Element.CAR: [Isotope.C12, Isotope.C13, Isotope.C14],
      Element.OXY: [Isotope.O17, Isotope.O16, Isotope.O18, Isotope.O16H1],
      Element.NEW_ELEMENT: [Isotope.NE1, Isotope.NE2]
   }
   ```

4. Create Ratio objects in `src/model/settings/methods_from_isotopes.py` where the first isotope is the numerator and the second is the denominator in the isotopic ratio. 
e.g.:
   ```python
   # Oxygen ratios
   O17_O16 = Ratio(Isotope.O17, Isotope.O16, has_delta=True)
   O18_O16 = Ratio(Isotope.O18, Isotope.O16, has_delta=True)
   O16H1_O16 = Ratio(Isotope.O16H1, Isotope.O16, has_delta=False)
      
   # New element ratios
   NE1_NE2 = Ratio(Isotope.NE1, Isotope.NE2, has_delta=True) 
   ```

5. Instantiate the new Method object and add it to the list of methods in `src/model/settings/methods_from_isotopes.py` e.g.:
    ```python
   three_isotopes_hydroxide_oxygen = Method([Isotope.O16, Isotope.O17, Isotope.O18, Isotope.O16H1],
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


5. Add the required delta notation constants into `src/model/settings/delta_constants.py` by adding an Enum in the DeltaReferenceMaterial class and then adding a dictionary for that material. Additionally, add the correct import statements for the new Ratio objects added in step 3.
e.g.:
   ```python
   from src/model/settings/methods_from_isotopes.py import [Ratios], NE1_NE2
   ```
   ```python
   class DeltaReferenceMaterial(Enum):
      VSMOW = 'VSMOW'
      VNEW = 'VNEW'
   ```
   ```python
   oxygen_isotope_reference = {
        DeltaReferenceMaterial.VSMOW: {O18_O16: 0.002005, O17_O16: 0.0003799}}
   
   new_element_isotope_reference = {
        DeltaReferenceMaterial.VNEW: {NE1_NE2: float, ISO_RATIO_2: float}}
    ```
   
6. Add the material list for the element into the material by element dictionary in `src/model/settings/material_lists.py` e.g.:
   ```python
   materials_by_element = {
      Element.OXY: [Material.ZIR, Material.QTZ],
      Element.NEW_ELEMENT: [Material.MAT]}
   ```

7. If Material.MAT does not already exist in the Material class in `src/model/settings/material_lists.py` then it must be added e.g.,:
   ```python
   class Material(Enum):
       ZIR = "Zircon"
       MAT = "Material"
   ```

8. Add the delta reference material to the Spot class in `src/model/spot.py` and additionally import the reference required.
   ```python
   from model.settings.delta_constants import oxygen_isotope_reference, sulphur_isotope_reference, new_element_isotope_reference
   ```
   ```python
   def calculate_raw_delta_for_isotope_ratio(self, element):
      
      if element == Element.OXY:
         standard_ratios = oxygen_isotope_reference[DeltaReferenceMaterial.VSMOW]
      elif element == Element.SUL:
         standard_ratios = sulphur_isotope_reference[DeltaReferenceMaterial.VCDT]
      elif element == Element.NEW_ELEMENT:
         standard_ratios = new_element_isotope_reference[DeltaReferenceMaterial.VNEW]
   ```