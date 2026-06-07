export async function slide01(presentation) {
  const slide = presentation.slides.add();
  const shape = slide.shapes.add({
    geometry: "rect",
    position: { left: 80, top: 80, width: 560, height: 120 },
    fill: "#FBF8EF",
    line: { fill: "#20221C", width: 1 },
  });
  console.log("SHAPE_PROTO", Object.getOwnPropertyNames(Object.getPrototypeOf(shape)));
  console.log("SHAPE_KEYS", Object.keys(shape));
  console.log("SHAPE_TOSTR", shape.toString?.());
  return slide;
}
