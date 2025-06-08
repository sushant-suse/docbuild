Implement Deliverable & Metadata classes

* Deliverable contains an ``etree._Element`` class and represents
  an interface to extract important values from the XML config
* Metadata is a dataclass that reads the output of "daps metadata" from a file
* Add test files for each class
* Add utility function :func:`~docbuild.utils.convert.convert2bool`