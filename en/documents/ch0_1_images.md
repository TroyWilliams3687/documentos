---
UUID: 17263a7e-b5c1-11eb-9fb7-a3fe2da49343

title: Images
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...

# Images {#sec:ch0_1_images-1}

It should be possible to accommodate local images stored with relative and absolute paths as well as images stored remotely. It doesn't make much sense in the work that we are doing to use images stored remotely. In any case, it should be possible to number the figures in a consistent manor, whether they are remote or local.

We will be using the syntax from [pandoc-fignos](https://github.com/tomduck/pandoc-fignos) to define the figure number and references that we'll use.

## [pandoc-fignos](https://github.com/tomduck/pandoc-fignos) Usage

To mark a figure for numbering, add an identifier to its attributes:
```
![Caption.](image.png){#fig:id}
```

The prefix `#fig:` is required. id should be replaced with a unique string composed of letters, numbers, dashes and underscores. If id is omitted then the figure will be numbered but unreferenceable. Alternatively, reference link attributes may be used.

To reference the figure, use:

```
@fig:id
```

or:

```
{@fig:id}
```

Curly braces protect a reference and are stripped from the output.

### Clever References

Writing markdown like:

```
See fig. @fig:id.
```

Is a bit redundant. `pandoc-fignos` supports "clever references" via single-character modifiers in front of a reference. Users can write:

```
See +@fig:id.
```

That will add the 'fig' portion automatically.

If the figure refernece is at the beginning of a sentence, use:

```
*@fig:id
```

If clever references are enabled, which by default they are (see Customization, below), they can be disabled by:

```
!@fig:id
```

>NOTE: Using the exclamation point disables the references on a per-reference basis.

### Tagged Figures

You can change the figure number of a reference by placing an appropriate tag value in the attribute block:

```
![Caption.](image.png){#fig:id tag="B.1"}
```

The tag can be arbitrary text, or an inline equation such as `$\text{B.1}'$`. You can use one form or the other, but not both at the same time.

### Disabling Links

To disable a link to a reference:

```
@fig:id{nolink=True}
```

## Examples

<!-- Use the pandoc-fignos syntax for marking figures up...  -->
<!-- {#fig:id} this goes at the end of the image link. -->
<!-- id should be replaced with a unique string composed of letters, numbers, dashes and underscores. -->
<!-- For me, I will use the name of the document and numbers. "ch0_preamble-1" -->
<!-- NOTE: You can specify height and width of the image - https://stackoverflow.com/questions/14675913/changing-image-size-in-markdown -->


![This is a sample image representing the VOD curve of a packaged watergel explosive.](./assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png){#fig:ch0_1_images-1 width=100%}

<!-- **\*@fig:ch0_1_images-1** - This is a sample image representing the VOD curve of a packaged Watergel explosive. -->

![Definition of a circular arc.](./assets/circle_arc.png){#fig:ch0_1_images-2}

<!-- **\*@fig:ch0_1_images-2** - Definition of a circular arc. -->