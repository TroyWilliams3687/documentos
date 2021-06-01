---
UUID: 6454025e-b5c1-11eb-9fb7-a3fe2da49343

title: Tables
language: en

version_created:
  date: 2021-05-15
  user: 2021.1
...

# Tables {#sec:ch0_3_tables-1}

It is quite common to display data in tabular form. Markdown has excellent support for simple tables. HTML tags can be used as well.


## [pandoc-tablenos](https://github.com/tomduck/pandoc-tablenos) Usage

To mark a table for numbering, add an id to its attributes:
```
A B
- -
0 1

Table: Caption. {#tbl:id}
```

The prefix `#tbl:` is required. `id` should be replaced with a unique identifier composed of letters, numbers, dashes and underscores. If id is omitted then the table will be numbered but unreferenceable.

To reference the table, use
```
@tbl:id
```

or
```
{@tbl:id}
```

Curly braces protect a reference and are stripped from the output.

### Clever References

Writing markdown like
```
See table @tbl:id.
```

seems a bit redundant. Pandoc-tablenos supports "clever references" via single-character modifiers in front of a reference. Users may write
```
 See +@tbl:id.
```

to have the reference name (i.e., "table") automatically generated. The above form is used mid-sentence. At the beginning of a sentence, use
```
 *@tbl:id
```

instead. If clever references are enabled by default (see Customization, below), then users may disable it for a given reference using4
```
!@tbl:id
```

Note: When using `*@tbl:id and emphasis (e.g., *italics*)` in the same sentence, the `*` in the clever reference must be backslash-escaped; e.g., `\*@tbl:id`.

### Tagged Tables

The table number may be overridden by placing a tag in the table's attributes block as follows:
```
A B
- -
0 1

Table: Caption. {#tbl:id tag="B.1"}
```

The tag may be arbitrary text, or an inline equation such as $\text{B.1}'$. Mixtures of the two are not currently supported.
Disabling Links

To disable a link on a reference, set nolink=True in the reference's attributes:
```
@tbl:id{nolink=True}
```

## Examples

|Name          | Value| Unit |
|--------------|------|------|
|Hole Diameter | 100  | mm   |
|Spacing       | 2.3  | m    |
|Burden        | 2    | m    |

Table: Pattern variables used in the model. {#tbl:ch0_3_tables-1}
<br>


|Name                         | Value            | Unit |
|-----------------------------|------------------|------|
|Explosive                    | SUBTEK INTENSE A |      |
|Charge Density               | 1.2              | g/cc |
|Charge Diameter              | 100              | mm   |
|Detonation Velocity          | 5723.2           | m/s  |
|Explosive Detonation Pressure| 10.0629856344    | GPa  |
|Thermochemical Pressure      | 5.0314928172     | GPa  |

Table: Explosive variables used in the model. {#tbl:ch0_3_tables-2}
<br>

|Name                         | Value              | Unit |
|-----------------------------|--------------------|------|
|Rock                         | ELEONORE WACKE - 2 |      |
|Static Tensile Strength      | 6.16               |  MPa |
|Static Compressive Strength  | 100.6907152714     |  MPa |
|P-Wave Velocity              | 6010               |  m/s |
|S-Wave Velocity              | 3400               |  m/s |
|Rock Density                 | 2.74               |  g/cc|

Table: Rock variables used in the model. {#tbl:ch0_3_tables-3}
<br>

|Name                         | Value         | Unit |
|-----------------------------|---------------|------|
|Time To Free Face            | 0.3327787022  |  ms  |
|Unit Charge Length           | 1.9045590682  |  m   |
|Unit Charge Volume           | 0.0149583719  |  m³  |
|Unit Charge Weight           | 17.9500463311 |  kg  |
|Unit Charge Energy           | 61.1343621979 |  MJ  |
|Unit Charge Internal Surface | 0.5983348777  |  m²  |
|Unit Charge Impulse          | 2.0036723058  |  MN·s|

Table: Unit Charge variables used in the model. {#tbl:ch0_3_tables-4}
<br>

|Name                                            | Value         | Unit      |
|------------------------------------------------|---------------|-----------|
|Dynamic Compressive Strength - PPV              | 15.3066735414 |  m/s      |
|Dynamic Tensile Strength - PPV                  | 0.936423073   |  m/s      |
|Static Compressive Strength - PPV               | 6.1145484576  |  m/s      |
|Static Tensile Strength - PPV                   | 0.3740724097  |  m/s      |
|Dynamic Compressive Strength SD                 | 0.4711489369  |  m/(kg¹/²)|
|Dynamic Tensile Strength SD                     | 0.0289352666  |  m/(kg¹/²)|
|Static Compressive Strength SD                  | 0.1889381999  |  m/(kg¹/²)|
|Static Tensile Strength SD                      |               |  m/(kg¹/²)|
|Dynamic Compressive Strength SD from Free Face  | 0.0009110703  |  m/(kg¹/²)|
|Dynamic Tensile Strength SD from Free Face      | 0.4431247407  |  m/(kg¹/²)|
|Static Compressive Strength SD from Free Face   | 0.2831218074  |  m/(kg¹/²)|
|Static Tensile Strength SD from Free Face       |               |  m/(kg¹/²)|
|Borehole Wall SD                                | 0.0118015002  |  m/(kg¹/²)|
|Free Face SD                                    | 0.4720600073  |  m/(kg¹/²)|
|Borehole Wall PPV                               | 611.0852735956|  m/s      |
|Borehole Wall Stress                            | 10.0629856344 |  GPa      |
|Free Face PPV                                   | 15.2771318399 |  m/s      |
|Free Face Stress                                | 251.5746408602|  MPa      |
|CSB/TSB Ratio                                   | 0.0266324561  |           |
|Distance From Free Face To DTS                  | 1.8774085237  |  m        |

Table: Stress Profile results calculated by the model. {#tbl:ch0_3_tables-5}
<br>


|Name                                   | Unit       | -30%                               | -15%                               | Mean                              | 15%                               | 30%                                |
|---------------------------------------|------------|------------------------------------|------------------------------------|-----------------------------------|-----------------------------------|------------------------------------|
|Pattern Extent Radius                  |   m        | 2.4897104269                       | 2.2583407476                       |2.0811322616                       |1.9397742096                       | 1.8235955076                       |
|Pattern Extent Tonnage                 |   t        | 101.6231279298                     | 83.6130033204                      |71.0058687512                      |61.6875104614                      | 54.5195056543                      |
|Pattern Extent Powder Factor - Volume  |   kg/m³    | 0.4839757243                       | 0.5882234221                       |0.6926628434                       |0.7972947292                       | 0.9021198259                       |
|Pattern Extent Powder Factor - Mass    |   kg/tonne | 0.176633476                        | 0.2146800811                       |0.2527966582                       |0.2909834778                       | 0.3292408124                       |
|Pattern Extent Energy Factor           |   MJ/m³    | 1.6483270672                       | 2.0033744247                       |2.3590747549                       |2.7154305818                       | 3.0724444474                       |
|Equivalent Pattern Spacing and Burden  |   m        | 4.73230464307263 x 4.11504751571533| 4.29252988226923 x 3.73263468023411|3.95570173875703 x 3.43974064239742|3.68701612829316 x 3.20610098112449| 3.46619004149002 x 3.01407829694784|

Table: Radial Break results calculated by the model. {#tbl:ch0_3_tables-6}
<br>

## Example References

We can see the properties in:

- Table @tbl:ch0_3_tables-1
- Table @tbl:ch0_3_tables-2
- Table @tbl:ch0_3_tables-3
- Table @tbl:ch0_3_tables-4

And the model calculations in:

- Table @tbl:ch0_3_tables-5
- Table @tbl:ch0_3_tables-6