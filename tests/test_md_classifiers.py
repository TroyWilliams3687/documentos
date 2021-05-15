#!/usr/bin/env python3
#-*- coding:utf-8 -*-

# -----------
# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Troy Williams

# uuid       = 0469cb3e-3007-11eb-bf3c-ab85e03a1801
# author     = Troy Williams
# email      = troy.williams@bluebill.net
# date       = 2020-11-26
# -----------

"""
"""

import pytest

from md_docs.markdown_classifiers import MarkdownLinkRule, AbsoluteURLRule, RelativeMarkdownURLRule, MarkdownImageRule, ATXHeaderRule, CodeFenceClassifier, HTMLImageRule

# -------------
# Test - MarkdownLinkRule - matches


data = []

data.append(('- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.', True))
data.append(('The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.', True))
data.append(('## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)', True))
data.append(('The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)', True))
data.append(('This string does not contain any links', False))
data.append(('[Definition of a circular arc.](../assets/circle_arc.png)', True))
data.append(('[Hyperbola](../../assets/HyperbolaAnatomyLeft.png)', True))


@pytest.mark.parametrize('data', data)
def test_md_link_rule_match(data):

    value, result = data
    rule = MarkdownLinkRule()

    assert rule.match(value) == result


data = []
data.append(('This string does not contain any links', None)
)

data.append(('- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.',
            [{'text':'pandoc-fignos', 'link':'https://github.com/tomduck/pandoc-fignos', 'full':'[pandoc-fignos](https://github.com/tomduck/pandoc-fignos)'}])
)

data.append(('## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)',
            [{'text':'Equations', 'link':'./ch0_2_equations.md#sec:ch0_2_equations-1', 'full':'[Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)'}])
)

data.append(('The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.',
            [{'text':'figure', 'link':'./ch0_1_images.md#fig:ch0_1_images-1', 'full':'[figure](./ch0_1_images.md#fig:ch0_1_images-1)'},
             {'text':'figure', 'link':'./ch0_1_images.md#fig:ch0_1_images-2', 'full':'[figure](./ch0_1_images.md#fig:ch0_1_images-2)'}])
)

data.append(('The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)',
            [{'text':'internal energy equation', 'link':'./ch0_2_equations.md#eq:ch0_2_equations-1', 'full':'[internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1)'},
             {'text':'detonation pressure', 'link':'./ch0_2_equations.md#eq:ch0_2_equations-2', 'full':'[detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)'}])
)


@pytest.mark.parametrize('data', data)
def test_md_link_rule_extraction(data):

    value, results = data
    rule = MarkdownLinkRule()

    output = rule.extract_data(value)

    assert output == results



# ----------
# Test AbsoluteURLRule

data = []

data.append(('https://github.com/tomduck/pandoc-fignos', True))
data.append(('http://github.com/tomduck/pandoc-fignos', True))
data.append(('ftp://github.com/tomduck/pandoc-fignos', True))

data.append(('http://github.com/ tomduck/ pandoc-fignos', False))
data.append(('ftp:// github.com/ tomduck/ pandoc-fignos', False))
data.append(('ftps://github.com/tomduck/pandoc-fignos', False))
data.append(('www.google.ca', False))
data.append(('google.com', False))

@pytest.mark.parametrize('data', data)
def test_absolute_url_rule_match(data):

    value, result = data
    rule = AbsoluteURLRule()

    assert rule.match(value) == result


data = []
data.append(('https://github.com/tomduck/pandoc-fignos', 'https://github.com/tomduck/pandoc-fignos'))
data.append(('http://github.com/tomduck/pandoc-fignos', 'http://github.com/tomduck/pandoc-fignos'))
data.append(('ftp://github.com/tomduck/pandoc-fignos', 'ftp://github.com/tomduck/pandoc-fignos'))

data.append(('http://github.com/ tomduck/ pandoc-fignos', None))
data.append(('ftp:// github.com/ tomduck/ pandoc-fignos', None))
data.append(('ftps://github.com/tomduck/pandoc-fignos', None))
data.append(('www.google.ca', None))
data.append(('google.com', None))

@pytest.mark.parametrize('data', data)
def test_absolute_url_rule_extraction(data):

    value, results = data
    rule = AbsoluteURLRule()

    output = rule.extract_data(value)

    assert output == results


# ---------------
# Test RelativeMarkdownURLRule

data = []
data.append(('https://github.com/tomduck/pandoc-fignos', False))
data.append(('http://github.com/tomduck/pandoc-fignos', False))
data.append(('ftp://github.com/tomduck/pandoc-fignos', False))
data.append(('ftp://github.com/ tomduck/ pandoc-fignos', False))
data.append(('ftp:// github.com/ tomduck/ pandoc-fignos', False))
data.append(('ftps://github.com/tomduck/pandoc-fignos', False))
# data.append(('www.google.ca', False))
# data.append(('google.com', False))


data.append(('./ch0_1_images.md#fig:ch0_1_images-1', True))
data.append(('./ch0_1_images.md#fig:ch0_1_images-2', True))
data.append(('./ch0_2_equations.md#sec:ch0_2_equations-1', True))
data.append(('./ch0_2_equations.md#eq:ch0_2_equations-1', True))
data.append(('./ch0_2_equations.md#eq:ch0_2_equations-2', True))
data.append(('./ch0_2_equations.md', True))
data.append(('./hello world.md', True))
data.append(('#eq:ch0_2_equations-2', True))
data.append(('#eq:ch0_2_equations-2', True))
data.append(('../assets/circle_arc.png', True))
data.append(('../../assets/HyperbolaAnatomyLeft.png', True))

@pytest.mark.parametrize('data', data)
def test_relative_md_url_rule_match(data):

    value, result = data
    rule = RelativeMarkdownURLRule()

    assert rule.match(value) == result


data = []
data.append(('https://github.com/tomduck/pandoc-fignos', None))
data.append(('http://github.com/tomduck/pandoc-fignos', None))
data.append(('ftp://github.com/tomduck/pandoc-fignos', None))
data.append(('ftp://github.com/ tomduck/ pandoc-fignos', None))
data.append(('ftp:// github.com/ tomduck/ pandoc-fignos', None))
data.append(('ftps://github.com/tomduck/pandoc-fignos', None))
# data.append(('www.google.ca', None))
# data.append(('google.com', None))

data.append(('./ch0_1_images.md#fig:ch0_1_images-1', {
                                                     'md':'./ch0_1_images.md',
                                                     'section':'#fig:ch0_1_images-1',
                                                     'md_span':(0, 17),
                                                     'section_span':(17, 36),
                                                     }))

data.append(('./ch0_1_images.md#fig:ch0_1_images-2', {
                                                     'md':'./ch0_1_images.md',
                                                     'section':'#fig:ch0_1_images-2',
                                                     'md_span':(0, 17),
                                                     'section_span':(17, 36),
                                                     }))

data.append(('./ch0_2_equations.md#sec:ch0_2_equations-1', {
                                                            'md':'./ch0_2_equations.md',
                                                            'section':'#sec:ch0_2_equations-1',
                                                            'md_span':(0, 20),
                                                            'section_span':(20, 42),
                                                            }))

data.append(('./ch0_2_equations.md#eq:ch0_2_equations-1',  {
                                                            'md':'./ch0_2_equations.md',
                                                            'section':'#eq:ch0_2_equations-1',
                                                            'md_span':(0, 20),
                                                            'section_span':(20, 41),
                                                            }))

data.append(('./ch0_2_equations.md#eq:ch0_2_equations-2',  {
                                                            'md':'./ch0_2_equations.md',
                                                            'section':'#eq:ch0_2_equations-2',
                                                            'md_span':(0, 20),
                                                            'section_span':(20, 41),
                                                            }))

data.append(('./ch0_2_equations.md',  {
                                       'md':'./ch0_2_equations.md',
                                       'section':None,
                                       'md_span':(0, 20),
                                       'section_span':(-1, -1),
                                       }))

data.append(('./hello world.md',      {
                                       'md':'./hello world.md',
                                       'section':None,
                                       'md_span':(0, 16),
                                       'section_span':(-1, -1),
                                       }))

data.append(('#eq:ch0_2_equations-2', {
                                       'md':'',
                                       'section':'#eq:ch0_2_equations-2',
                                       'md_span':(0, 0),
                                       'section_span':(0, 21),
                                       }))
data.append(('#eq:ch0_2_equations-1', {
                                       'md':'',
                                       'section':'#eq:ch0_2_equations-1',
                                       'md_span':(0, 0),
                                       'section_span':(0, 21),
                                       }))


@pytest.mark.parametrize('data', data)
def test_relative_md_url_rule_extraction(data):

    value, results = data
    rule = RelativeMarkdownURLRule()

    output = rule.extract_data(value)

    assert output == results


# --------------
# Test MarkdownImageRule


data = []

data.append(('- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.', False))
data.append(('The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.', False))
data.append(('## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)', False))
data.append(('The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)', False))
data.append(('This string does not contain any links', False))


data.append(('![Caption.](image.png){#fig:id}', True))
data.append(('![Caption.](image.png){#fig:id tag="B.1"}', True))
data.append(('![This is a sample image representing the VOD curve of a packaged Watergel explosive.](../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png){#fig:ch0_1_images-1 width=100%}', True))
data.append(('![](../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png)', True))
data.append(('![](../../assets/XwMrG0o__iLF5nStoSPUuJ81ffxafRBWAVnEcGo10Yo=.png) and another image: ![test](image.png)', True))


@pytest.mark.parametrize('data', data)
def test_md_image_rule_match(data):

    value, result = data
    rule = MarkdownImageRule()

    assert rule.match(value) == result

data = []
data.append(('- [pandoc-fignos](https://github.com/tomduck/pandoc-fignos): Numbers figures and figure references.', None))
data.append(('The images section will walk you through how to add and reference images so that the pandoc system can properly number them. For example, this [figure](./ch0_1_images.md#fig:ch0_1_images-1) illustrates a VOD curve for a packaged watergel explosive and this [figure](./ch0_1_images.md#fig:ch0_1_images-2) depicts a circular arc.', None))
data.append(('## [Equations](./ch0_2_equations.md#sec:ch0_2_equations-1)', None))
data.append(('The equations section will discuss how to use equations and reference them properly. See the [internal energy equation](./ch0_2_equations.md#eq:ch0_2_equations-1) or the [detonation pressure](./ch0_2_equations.md#eq:ch0_2_equations-2)', None))
data.append(('This string does not contain any links', None))

data.append(('![Caption.](image.png){#fig:id}',           [{'caption':'Caption.', 'image':'image.png'}]))
data.append(('![Caption.](image.png){#fig:id tag="B.1"}', [{'caption':'Caption.', 'image':'image.png'}]))


data.append(('![This is a sample image representing the VOD curve of a packaged Watergel explosive.](../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png){#fig:ch0_1_images-1 width=100%}', [{'caption':'This is a sample image representing the VOD curve of a packaged Watergel explosive.', 'image':'../assets/1v6C9yek3pHsXSeOlR4glzDMkFqFHizR6VXr79tEOnY=.png'}]))
data.append(('![](../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png)', [{'caption':'', 'image':'../../assets/E5WnRoSH_Dqrzl8f5_ZJ9AjWc-53BgiBqD_xTqEp6pM=.png'}]))

data.append(('![This Image](image1.png) and another image ![That Image](image2.png)',
             [{'caption':'This Image', 'image':'image1.png'},
             {'caption':'That Image', 'image':'image2.png'}]))


@pytest.mark.parametrize('data', data)
def test_md_image_rule_extraction(data):

    value, results = data
    rule = MarkdownImageRule()

    output = rule.extract_data(value)

    if results is None:
        assert results == output

    else:

        for r,o in zip(results, output):
            assert r['caption'] == o['caption']
            assert r['image'] == o['image']

    # assert output == results

# ----------
# ATXHeaderRule - ATX level 1

data = []
data.append(('# Test', True))
data.append(('# Hello World', True))
data.append(('# #Admin - Test', True))

data.append(('# Hello World', True))
data.append((' # Hello World', True))
data.append(('  # Hello World', True))
data.append(('   # Hello World', True))
data.append(('    # Hello World', False))
data.append(('     # Hello World', False))


data.append(('    # Test     ', False))
data.append((' ## Test', False))
data.append(('Hello # Test', False))
data.append(('## Test', False))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_1(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=1)

    assert rule.key == key
    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization
    assert rule.is_full_match == False


# ---------
# Test - ATXHeaderRule - 2

data = []
data.append(('## Test', True))
data.append(('## Hello World', True))
data.append(('## #Admin - Test', True))
data.append((' ## Test', True))

data.append(('    ## Test     ', False))
data.append(('Hello ## Test', False))
data.append(('### Test', False))
data.append(('# Test', False))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_2(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=2)

    assert rule.key == key
    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization
    assert rule.is_full_match == False


# ---------
# Test - ATXHeaderRule - 3

data = []
data.append(('### Test', True))
data.append(('### Hello World', True))
data.append(('### #Admin - Test', True))
data.append((' ### Test', True))

data.append(('    ### Test     ', False))
data.append(('Hello ### Test', False))
data.append(('#### Test', False))
data.append(('## Test', False))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_3(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=3)

    assert rule.key == key
    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization
    assert rule.is_full_match == False


# ---------
# Test - ATXHeaderRule - 4

data = []
data.append(('#### Test', True))
data.append(('#### Hello World', True))
data.append(('#### #Admin - Test', True))
data.append((' #### Test', True))

data.append(('    #### Test     ', False))
data.append(('Hello #### Test', False))
data.append(('##### Test', False))
data.append(('### Test', False))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_4(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=4)

    assert rule.key == key
    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization
    assert rule.is_full_match == False


# ---------
# Test - ATXHeaderRule - 5

data = []
data.append(('##### Test', True))
data.append(('##### Hello World', True))
data.append(('##### #Admin - Test', True))
data.append((' ##### Test', True))

data.append(('    ##### Test     ', False))
data.append(('Hello ##### Test', False))
data.append(('###### Test', False))
data.append(('#### Test', False))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_5(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=5)

    assert rule.key == key
    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization
    assert rule.is_full_match == False

# ---------
# Test - ATXHeaderRule - 6

data = []
data.append(('###### Test', True))
data.append(('###### Hello World', True))
data.append(('###### #Admin - Test', True))
data.append((' ###### Test', True))

data.append(('    ###### Test     ', False))
data.append(('Hello ###### Test', False))
data.append(('####### Test', False))
data.append(('##### Test', False))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_6(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=6)

    assert rule.key == key
    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization
    assert rule.is_full_match == False

# ---------
# Test - ATXHeaderRule - exception

def test_atxheader_rule_error():

    key = 'Hello asdfasdf'

    with pytest.raises(ValueError):
        rule = ATXHeaderRule(key=key, count=0)

    with pytest.raises(ValueError):
        rule = ATXHeaderRule(key=key, count=7)

    with pytest.raises(ValueError):
        rule = ATXHeaderRule(key=key, count=-1)


# -----------
# Test - ATXHeaderRule - 1 - Extract Data

data = []
data.append(('# Test'           , 'Test'))
data.append(('# Hello World'    , 'Hello World'))
data.append(('# #Admin - Test'  , '#Admin - Test'))

data.append(('    # Test     ', None))
data.append((' ## Test'       , None))
data.append(('Hello # Test'   , None))
data.append(('## Test'        , None))

@pytest.mark.parametrize('data', data)
def test_atxheader_rule_1_data(data):

    key = 'Hello asdfasdf'
    value, result = data
    rule = ATXHeaderRule(key=key, count=1)

    assert rule.key == key

    assert rule.extract_data(value) == result
    assert rule.extract_data(value) == result # test memoization

    assert rule.is_full_match == False

# ----------------
# Test - CodeFenceClassifier

data = []

    # ```   bash hello world
        # ``` bash hello world
        # ~~~    python
        # ~~~
        # ```
        #                         ```````` hello

data.append(('```   bash hello world', True))
data.append(('``` bash hello world'  , True))
data.append(('~~~' , True))
data.append(('     ~~~   ' , True))
data.append(('```' , True))
data.append(('```    ' , True))
data.append(('```    python' , True))
data.append(('     ```    python' , True))
data.append(('     ``````    python' , True))
data.append(('  ~~~~    python' , True))
data.append(('```````python' , True))

data.append(('     ``~`    python' , False))
data.append(('     `~~`    python' , False))
data.append(('     ``~`    python' , False))

@pytest.mark.parametrize('data', data)
def test_codefenceclassifier(data):

    key = 'xx 12345'
    value, result = data
    rule = CodeFenceClassifier(key=key)

    assert rule.key == key

    assert rule.match(value) == result
    assert rule.match(value) == result # test memoization

    assert rule.is_full_match == True


# --------------
# Test HTMLImageRule


data = []

data.append(('<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>', True))
data.append(('<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>'    , True))
data.append(('<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/> '   , True))
data.append(('<img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>'                            , True))

data.append(('<img src="hello world"/> <img /> <img src="hello world"/>'                                    , True))

data.append(('<img alt="Similar Triangles" style="width: 600px;"/>'                                         , False))
data.append(('<img/>'                                                                                       , False))

@pytest.mark.parametrize('data', data)
def test_html_image_rule_match(data):

    question, answer = data
    rule = HTMLImageRule()

    assert rule.match(question) == answer


data = []

data.append(('<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>', [{'full':'<img src="../../assets/similar_triangles.png" alt="Similar Triangles" style="width: 600px;"/>', 'src':'../../assets/similar_triangles.png'}]))
data.append(('<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>'    , [{'full':'<img src="../../assets/break_out_angle.png" alt="break out angle" style="width: 400px;"/>', 'src':'../../assets/break_out_angle.png'}]))
data.append(('<img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>'                            , [{'full':'<img src="azimuth_dump.png" alt="Drawing" style="width: 200px;"/>', 'src':'azimuth_dump.png'}]))
data.append(('<img src="hello world"/> <img /> <img src="hello world2"/>'                                    , [{'full':'<img src="hello world"/>', 'src':'hello world'}, {'full':'<img src="hello world2"/>', 'src':'hello world2'}]))

data.append(('<img alt="Similar Triangles" style="width: 600px;"/>'                                         , None))
data.append(('<img/>'                                                                                       , None))


@pytest.mark.parametrize('data', data)
def test_html_image_rule_extraction(data):

    question, answer = data
    rule = HTMLImageRule()

    output = rule.extract_data(question)

    assert output == answer
