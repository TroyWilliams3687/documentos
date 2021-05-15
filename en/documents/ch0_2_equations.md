---
ID: 4d2d5d64-b5c1-11eb-9fb7-a3fe2da49343

title: Equations
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...


# Equations {#sec:ch0_2_equations-1}

Equations are a bit different. Pandoc markdown supports equations using the \$ delimiters. In-line equations are denoted with single \$ at each end. For example, this would be inline: `$Y = mx^2 + \frac{b}{a}$` yielding: $Y = mx^2 + \frac{b}{a}$.

While this is not in-line:
```
$$ Y = mx^2 + \frac{b}{a}$$
```

Producing:

$$ Y = mx^2 + \frac{b}{a}$$

The latex conventions are followed, any good reference site can be used.


## [pandoc-eqnos](https://github.com/tomduck/pandoc-eqnos) Usage

To mark an equation for numbering, add an identifier to its attributes:

```
$$ y = mx + b $$ {#eq:id}
```

The prefix `#eq:` is required. `id` should be replaced with a unique string composed of letters, numbers, dashes and underscores. If id is omitted then the equation will be numbered but unreferenceable.

To reference the equation, use
```
@eq:id
```

or
```
{@eq:id}
```

Curly braces protect a reference and are stripped from the output.

### Clever References

Writing markdown like
```
See eq. @eq:id.
```

seems a bit redundant. Pandoc-eqnos supports "clever references" via single-character modifiers in front of a reference. You can write
```
See +@eq:id.
```

to have the reference name (i.e., "eq.") automatically generated. The above form is used mid-sentence; at the beginning of a sentence, use
```
*@eq:id
```

instead. If clever references are enabled by default (see Customization, below), then users may disable it for a given reference using4
```
!@eq:id
```

Note: When using `*@eq:id and emphasis (e.g., *italics*)` in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*@eq:id`.

### Tagged Equations

The equation number may be overridden by placing a tag in the equation's attributes block:
```
$$ y = mx + b $$ {#eq:id tag="B.1"}
```

The tag may be arbitrary text, or an inline equation such as `$\mathrm{B.1'}$`. Mixtures of the two are not currently supported.
Disabling Links

To disable a link on a reference, set nolink=True in the reference's attributes:
```
@eq:id{nolink=True}
```

## Examples

### Internal Energy, $E_{i}$

$$E_{i} = \rho_{e}\cdot W \cdot \left( \frac{V_{e}}{V_{ideal}} \right)^{2}$$ {#eq:ch0_2_equations-1}

Equation @eq:ch0_2_equations-1, Where:

- $E_{i}$ - Internal Energy $\left( \frac{J}{m^3} \right)$
- $\rho_{e}$ - Explosive Density $\left( \frac{kg}{m^3} \right)$
- $W$ - Absolute Weight Strength - $\left( \frac{J}{kg} \right)$
- $V_{e}$ - Velocity of detonation $\left( \frac{m}{s} \right)$
- $V_{ideal}$ - Ideal velocity $\left( \frac{m}{s} \right)$

### Explosive Detonation Pressure, $P_{id}$

$$P_{id} = \frac{\rho_{e} \cdot V_{e}^2}{\gamma_{cj}}$$ {#eq:ch0_2_equations-2}

Equation @eq:ch0_2_equations-2, Where:

- $P_{id}$ - Intrinsic Detonation Pressure $\left( Pa \right)$
- $\rho_{e}$ - Explosive Density $\left( \frac{g}{cm^3} \right)$
- $V_{e}$ - Velocity of detonation $\left( \frac{m}{s} \right)$
- $\gamma_{cj}$ - Gamma CJ

### Borehole Pressure, $P_{dbp}$

$$P_{dbp} = \frac{P_{id}}{2} \cdot \left( \frac{\oslash_{ED}}{\oslash_{BD}} \right)^{\epsilon} \cdot \sqrt{\frac{L_e}{L_b}}$$ {#eq:ch0_2_equations-3}

Equation @eq:ch0_2_equations-3, Where:

- $P_{dbp}$ - Borehole Pressure $\left( Pa \right)$
- $P_{id}$ - Detonation Pressure $\left( Pa \right)$
- $\oslash_{ED}$ - Explosive charge diameter $(mm)$
- $\oslash_{BD}$ - Borehole diameter $(mm)$
- $\epsilon$ - Ratio of specific heats
- $L_e$ - Length of explosive column $(m)$
- $L_b$ - Length of borehole column $(m)$

### References

- Equation @eq:ch0_2_equations-1
- Equation @eq:ch0_2_equations-2
- Equation @eq:ch0_2_equations-3