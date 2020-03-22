Core Widgets
============

We refer to the widgets that are bundled with Jibe as the
Core Widgets. This is a minimal collection of widgets that
allow you to compose the great majority of more complex
widgets, simply by combining them together.

Contents:

.. contents:: :local:

Widget
------

All other widgets inherit from the Widget class. By itself
it is of little use, but it serves as a blank canvas to build
other widgets from scratch, at a low level. For most applications
you will not need to use this class directly, instead, you will
inherit from other widgets and will customize their behavior.
See the Widget API for more details.

Div
---

This is identical to Widget. It represents a ``<div> … </div>``
in the DOM (a plain empty container in your page).

Button
------

A button. Represents a ``<button> … </button>`` in the DOM.
It has 1 property: `label`, which is displayed on the face of
the button, and triggers 1 event: `click`.

.. code-block:: python

    btn = Button('button')
    btn.register('click', click_handler)

.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    button.widget {
        color: rgba(0,0,0,0.8);
        background-color: #eaeaea;
        padding: 6px 10px;  /* Top-bottom right-left */
        margin: 8px;
        border-width: 0;
        cursor: pointer;
    }
    button.widget:hover {
        box-shadow: 3px 3px 3px #a4a4a4;
    }

    button.widget:active {
        box-shadow: 0px 0px 0px #a4a4a4;
    }

    button.widget:focus {
        outline: 1px solid #709aa4;
    }
    </style>
    <button class="widget button" id="Button-qxmpomugb0">button</button>


Input
-----

A single-line text input. It represents an ``<input>`` in the DOM.
It has 1 property: `value`, and triggers 1 event: `change`.

.. code-block:: python

    input = Input('input')
    input.register('change', change_handler)

.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    input.widget {
        border-color: rgb(158,158,158);
        border-style: solid;
        border-width: 1px;
        padding: 4px;
        margin: 8px;
        box-shadow: inset 0 1px 3px #ddd;

        font-size: 13px;
        color: rgba(0,0,0,0.8);
    }
    </style>
    <input class="widget input" id="Input-1ud6qv7mo8" value="input">


Label
-----

A simple text label. It has 1 property: `value`, and no events.
It represents a ``<div><p> ... </p></div>`` structure in the DOM.

.. code-block:: python

    label = Label('I am a label')

.. raw:: html

    <style>
        .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    .widget.label {
        display: table-cell;
        vertical-aligh: middle;
    }
    </style>
    <div class="widget label"><p>I am a label</p></div>


CheckBox
--------

A check box. It represents a ``<input type="checkbox"/>`` in the DOM.
It has one property: `checked` and triggers one event: `change`.

.. code-block:: python

    chk = CheckBox()
    chk.register('change', on_change)

.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    .widget.checkbox {
        margin: auto 4px auto 4px;
    }
    </style>
    <input class="widget checkbox" type="checkbox" id="CheckBox-pk3qf6mlem">


Dropdown
--------

A selection drop-down. It represents a ``<select> ... </select>`` in the DOM.
It has two properties: `value` and `options`, and triggers one event: `change`.

.. code-block:: python

    dropdown = Dropdown(
        options=[
            'apples',
            'banannas',
            'chocolate'
        ]
    )
    dropdown.register('change', on_change)

.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    select.widget {
        border-color: rgb(158,158,158);
        border-style: solid;
        border-width: 1px;
        padding: 4px;
        margin: 8px;
        /*box-shadow: inset 0 1px 3px #ddd;*/

        font-size: 13px;
        color: rgba(0,0,0,0.8);
        background-color: rgba(255,255,255,0.8);
    }
    select.widget:focus {
        outline: 1px solid #709aa4;
    }
    </style>
    <select class="widget dropdown" id="Dropdown-4y1iz4mkv6">
            <option value="apples" selected="">apples</option>
            <option value="banannas">banannas</option>
            <option value="chocolate">chocolate</option>
    </select>


SelectMultiple
--------------

A multiple-selection list. It represents a
``<select multiple="multiple"> ... </select>`` in the DOM.
It has two properties: `value` and `options`.

.. code-block:: python

    sel = SelectMultiple(
        options=[
            'apples',
            'banannas',
            'chocolate'
        ]
    )
    sel.register('change', on_change)

.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    select.widget {
        border-color: rgb(158,158,158);
        border-style: solid;
        border-width: 1px;
        padding: 4px;
        margin: 8px;
        /*box-shadow: inset 0 1px 3px #ddd;*/

        font-size: 13px;
        color: rgba(0,0,0,0.8);
        background-color: rgba(255,255,255,0.8);
    }
    select.widget:focus {
        outline: 1px solid #709aa4;
    }
    </style>
    <select class="widget selectmultiple" multiple="multiple" id="SelectMultiple-tlcxphglt0">
            <option value="apples">apples</option>
            <option value="banannas">banannas</option>
            <option value="chocolate">chocolate</option>
    </select>


ProgressBar
-----------

Simple horizontal progress bar. It has one property: `value`, which
represents the percentage of completion (0 to 100). This is a composite
widget (a ``Div`` of fixed size for the background and another ``Div``
with variable width for the progress). It is not a "core" widget, since
you can build it yourself from other core widgets, but it is provided
as a example.

.. code-block:: python

    bar = ProgressBar(30)


.. raw:: html

    <div class="widget progressbar" id="ProgressBar-pnt5wv2df7" style="min-width: 300px; max-width: 300px; min-height: 28px; max-height: 28px; padding: 0px; border: 0px; margin: 8px; background-color: rgb(221, 221, 221);"><div class="widget div" id="Div-9xlswt059j" style="min-width: 30%; max-width: 30%; min-height: 28px; max-height: 28px; padding: 0px; border: 0px; margin: 0px; background-color: rgb(99, 99, 210);"></div></div>


Image
-----

An image/png. It represents a ``<img/>`` in the DOM and has one
property: `data`. The `data` is the image data, as a base64-encoded utf8 string
(see the code below).

.. code-block:: python

    import base64
    with open("image.png", "rb") as img:
        data = base64.encodebytes(img.read()).decode('utf8')

    img = Image()
    img.data = data


.. image:: image.png


Redirect
--------

An invisible widget that allows redirecting the browser to a
different url.

.. code-block:: python

    redir = Redirect()

    redir.redirect('/other')


HBox
----

A container widget that arrange its children horizontally. It does not
have any properties or events.

.. code-block:: python

    hbox = HBox()
    hbox.children = [
        Button('Left'), Button('Right')
    ]


.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    button.widget {
        color: rgba(0,0,0,0.8);
        background-color: #eaeaea;
        padding: 6px 10px;  /* Top-bottom right-left */
        margin: 8px;
        border-width: 0;
        cursor: pointer;
    }

    button.widget:hover {
        box-shadow: 3px 3px 3px #a4a4a4;
    }

    button.widget:active {
        box-shadow: 0px 0px 0px #a4a4a4;
    }

    button.widget:focus {
        outline: 1px solid #709aa4;
    }
    </style>
    <div class="widget hbox" id="HBox-u0dtbl909w" style="display: flex; flex-direction: row;"><button class="widget button" id="Button-mn02b1uhfg">Left</button><button class="widget button" id="Button-e3fqbca7n3">Right</button></div>


VBox
----

Same a ``HBox`` but vertical.

.. code-block:: python

    vbox = VBox()
    vbox.children = [
        Button('Top'), Button('Bottom')
    ]

.. raw:: html

    <style>
    .widget {
        font-family: "Lato","proxima-nova","Helvetica Neue",Arial,sans-serif;
        font-size: 13px;
        margin: 0px;
    }
    button.widget {
        color: rgba(0,0,0,0.8);
        background-color: #eaeaea;
        padding: 6px 10px;  /* Top-bottom right-left */
        margin: 8px;
        border-width: 0;
        cursor: pointer;
    }

    button.widget:hover {
        box-shadow: 3px 3px 3px #a4a4a4;
    }

    button.widget:active {
        box-shadow: 0px 0px 0px #a4a4a4;
    }

    button.widget:focus {
        outline: 1px solid #709aa4;
    }
    </style>
    <div class="widget vbox" id="VBox-ko1lx0uef5" style="display: flex; flex-direction: column;"><button class="widget button" id="Button-ps9athrp52">Top</button><button class="widget button" id="Button-dmsivydsfh">Bottom</button></div>