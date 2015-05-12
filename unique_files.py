import datetime
import os
import math


def create_unique_filename(directory=".", suffix=None, ext=""):
  if suffix is None:
    suffix = str(datetime.date.today())
  
  # If extension is not default or not empty, then the user has supplied
  #  a custom extension. If this custom extension does not start with a period
  #  then we prefix the extension with a period.
  if ext and (ext[0] != "."):
    ext = "."+ext
  
  files = [f for f in os.listdir(directory) if f.startswith(suffix)]
  n = len(files)
  
  if (n == 0):
    return os.path.join(directory, "{0}{1}".format(suffix, ext))
  
  if (n == 1):
    # The existing file is of the format "${date}.tiff". We need to rename it
    #  in the format "${date}_0.tiff".
    os.rename(
      os.path.join(directory, files[0]),
      os.path.join(directory, "{0}_0{1}".format(suffix, ext))
    )
    return os.path.join(directory, "{0}_1{1}".format(suffix, ext))
  
  else:  
    num_digits_needed_for_another_file = int(math.ceil(math.log10(n+1)))
    num_digits_used_for_current_files = int(math.ceil(math.log10(n)))
    if (num_digits_needed_for_another_file != num_digits_used_for_current_files):
      # Adding another file would require another digits in the filename
      #  sequence. We need to rename all files to add this extra digit before
      #  creating the new file.
      for i in range(n):
        old_file_number = str(i).zfill(num_digits_used_for_current_files)
        old_filename = "{0}_{1}{2}".format(suffix, old_file_number, ext)
        new_file_number = str(i).zfill(num_digits_needed_for_another_file)
        new_filename = "{0}_{1}{2}".format(suffix, new_file_number, ext)
        os.rename(
          os.path.join(directory, old_filename),
          os.path.join(directory, new_filename)
        )
    
  filename = "{0}_{1}{2}".format(suffix, n, ext)
  return os.path.join(directory, filename)


if __name__ == "__main__":
  # Test unique filename creation
  common_suffix = "b"
  extension = "tiff"
  directory = "/tmp"
  
  expected = os.path.join(
    directory,
    "{0}.{1}".format(common_suffix, extension)
  )
  actual = create_unique_filename(
    directory=directory,
    suffix=common_suffix,
    ext=extension
  )
  assert expected == actual, "Expected filename {0} does not match actual filename {1}".format(expected, actual)
  print("No existing files produces expected filename")
  
  ############################################################################
  # Test correctness of code if one file already exists.
  # Touch a file, and leave it empty.
  old_initial_file = expected
  open(old_initial_file, "a").close()
  
  expected = os.path.join(
    directory,
    "{0}_1.{1}".format(common_suffix, extension)
  )
  actual = create_unique_filename(
    directory=directory,
    suffix=common_suffix,
    ext=extension
  )
  assert expected == actual, "Expected filename {0} does not match actual filename {1}".format(expected, actual)
  print("Pre-existing file causes new unique filename")
  
  expected_moved_old_file = os.path.join(
    directory,
    "{0}_0.{1}".format(common_suffix, extension)
  )
  assert os.path.exists(expected_moved_old_file), "Pre-existing file {0} was not moved to {1}".format(old_initial_file, expected_moved_old_file)
  print("Pre-existing file was successfully moved")
  
  ############################################################################
  # Test correctness of code if two files already exists.
  # Touch a file, and leave it empty.
  existing_second_file = expected
  open(existing_second_file, "a").close()
  
  expected = os.path.join(
    directory,
    "{0}_2.{1}".format(common_suffix, extension)
  )
  actual = create_unique_filename(
    directory=directory,
    suffix=common_suffix,
    ext=extension
  )
  assert expected == actual, "Expected filename {0} does not match actual filename {1}".format(expected, actual)
  print("Pre-existing file causes new unique filename")
  
  expected_0_old_file = os.path.join(
    directory,
    "{0}_0.{1}".format(common_suffix, extension)
  )
  assert os.path.exists(expected_0_old_file), "Pre-existing file {0} was not moved to {1}".format(old_initial_file, expected_moved_old_file)
  
  expected_1_old_file = os.path.join(
    directory,
    "{0}_1.{1}".format(common_suffix, extension)
  )
  assert os.path.exists(expected_1_old_file), "Pre-existing file {0} was not moved to {1}".format(old_initial_file, expected_moved_old_file)
  print("Pre-existing files were not renamed if two pre-existing files were present")
  
  ############################################################################
  # Test correctness of code if 10 files already exists.
  # Touch a file, and leave it empty.
  second_file = expected
  for i in range(2, 10):
    created_file = os.path.join(
      directory,
      "{0}_{2}.{1}".format(common_suffix, extension, i)
    )
    open(created_file, "a").close()
  
  expected = os.path.join(
    directory,
    "{0}_10.{1}".format(common_suffix, extension)
  )
  actual = create_unique_filename(
    directory=directory,
    suffix=common_suffix,
    ext=extension
  )
  assert expected == actual, "Expected filename {0} does not match actual filename {1}".format(expected, actual)
  print("Pre-existing files cause new unique filename")
  
  # Verify files have been moved.
  for i in range(0, 10):
    expected_renamed_file = os.path.join(
      directory,
      "{0}_0{2}.{1}".format(common_suffix, extension, i)
    )
    assert os.path.exists(expected_renamed_file), "Pre-existing file was not moved to {0}".format(expected_renamed_file)
  print("Pre-existing files were not renamed if two pre-existing files were present")
  
  # Remove created files.
  for i in range(0, 10):
    delete_file = os.path.join(
      directory,
      "{0}_0{2}.{1}".format(common_suffix, extension, i)
    )
    os.remove(delete_file)
