#version 120

// attribute means distinct to the vertex
// the last token is the variable name
attribute highp vec4 vertex;
// uniform means distinct for each primitive?
// highp means high precision number it's the variable type basically
// mat4 means a matrix of size 4x4
uniform highp mat4 matrix;
// lowp means low precision number
// this is a vector of 4, vectors are lists basically
attribute lowp vec4 color_attr;
// varying means distinct for each fragment?
varying lowp vec4 color;


// declaring a variable with the attribute or uniform implicitly makes it an input variable
// declaring it as varying implicitly makes it an output variable
void main(void) {
// this is our global position??
    gl_Position = matrix * vertex;
//  this lets us specifiy the color
    color = color_attr;
                                                   }