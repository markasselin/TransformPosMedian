cmake_minimum_required(VERSION 3.5)

project(TransformPosMedian)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/TransformPosMedian")
set(EXTENSION_CATEGORY "TransformPosMedian")
set(EXTENSION_CONTRIBUTORS "Mark Asselin (PerkLab)")
set(EXTENSION_DESCRIPTION "Computes the median of position given by tracker over 5 seconds. Also exports the data set as csv file.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/TransformPosMedian.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/TransformPosMedian/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Dof3Median)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
