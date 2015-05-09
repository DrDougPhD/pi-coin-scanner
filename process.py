from cv import img2bounding_box

def merge(img1, img2):
  pass


if __name__ == "__main__":
  testing_samples = [
    ("sample/002.tiff", "sample/003.tiff"),
    ("sample/2015-05-08_1.tiff", "sample/2015-05-08_2.tiff")
  ]

  border_reduction = 50
  for (url1, url2) in testing_samples:
    side1 = img2bounding_box(url=url1, border_reduction=border_reduction)
    side2 = img2bounding_box(url=url2, border_reduction=border_reduction)

    for ingot1, ingot2 in zip(side1, side2)
      img1 = ingot1[0]
      img2 = ingot2[0]
      merged = merge(img1, img2)
      print("#"*80)
      print("{0} and {1} => {2}".format(img1, img2, merged))
      print("#"*80)

    if len(side2) != len(side1):
      print(
        "For the two scans, the number of split images is not equal "
        "({0} vs {1})".format(
          len(side1), len(side2)
      ))

