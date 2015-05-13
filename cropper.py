
class CroppingBox:
  def __init__(self, x, y, w, h):
    self.x = x
    self.y = y
    self.w = w
    self.h = h

  def area(self):
    return self.w * self.h

  def expand(self, border):
    box = CroppingBox(
      x=self.x-border,
      y=self.y-border,
      w=(self.w+(2*border)),
      h=(self.h+(2*border)),
    )
    print("Expanding borders of {0} by {1} pixels".format(self, border))
    return box

  def getCorners(self):
    return {
      "min_x": self.x,
      "max_x": self.x+self.w,
      "min_y": self.y,
      "max_y": self.y+self.h,
    }

  def __str__(self):
    return "<CroppingBox(area={0}, w={1}, h={2}, upper_left={3}, lower_right={4})>".format(
      self.area(),
      self.w,
      self.h,
      (self.x, self.y),
      (self.x+self.w, self.y+self.h),
    )

