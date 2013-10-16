'''
  ____                      _                      _
 / ___| _ __   ___  ___  __| | ___  _ __ ___   ___| |_ ___ _ __
 \___ \| '_ \ / _ \/ _ \/ _` |/ _ \| '_ ` _ \ / _ \ __/ _ \ '__|
  ___) | |_) |  __/  __/ (_| | (_) | | | | | |  __/ ||  __/ |
 |____/| .__/ \___|\___|\__,_|\___/|_| |_| |_|\___|\__\___|_|
       |_|

by Alan Fregtman - http://darkvertex.com (first version: Oct 15 2013.)

--------------------------------------------------------

The MIT License (MIT)

Copyright (c) 2013 Alan Fregtman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
from win32com.client import constants as C
xsi = Application

# =============================================================================

scop_JS = r'''
// Speedometer SCOP by Alan Fregtman - http://darkvertex.com

function SpeedometerOp_Update( In_UpdateContext, Out, Inglobal )
{

    // Initialize stuff
    var Inglobal = Inglobal.Value;
    var params = In_UpdateContext.Operator.Parameters;
    var scaleFactor = params("one_metre_equals").Value;
    var global_xform = Inglobal.Transform;
    var framerate = params("framerate").Value;
    var current_pos = global_xform.Translation;

    // We'll use UserData to store info between each eval:
    var data = In_UpdateContext.UserData;
    if (data == null) {
        data = new Object();
        data.last_pos = global_xform.Translation;
        data.resetBubbleOffset = false;
    }

    // How much did we move since last eval?
    var movement = XSIMath.CreateVector3();
    movement.Sub(current_pos, data.last_pos);
    var dist = movement.Length();

    // Convert to real-world units:
    var unitsPerSecond = dist * framerate;
    var metresPerSecond = unitsPerSecond / scaleFactor;
    var feetPerSecond = metresPerSecond * 3.28084;
    var kmh = metresPerSecond * 3.6;
    var mph = metresPerSecond * 2.237;
    var knots = metresPerSecond * 0.514; // international knot, fyi.
    var mach = metresPerSecond / 330.0; // divide by speed of sound.

    // "Mach" number in text. -- Has your object gone... sonic?! :o
    if (mach < 0.8) {
        var mach_txt = 'subsonic';
    } else if (mach >= 0.8 && mach <= 1.2) {
        var mach_txt = 'transonic';
    } else if (mach >= 1.2 && mach <= 5.0) {
        var mach_txt = 'supersonic';
    } else if (mach >= 5.0 && mach <= 10.0) {
        var mach_txt = 'hypersonic';
    } else if (mach >= 10.0 && mach <= 25.0) {
        var mach_txt = 'high-hypersonic';
    } else if (mach > 25.0) {
        var mach_txt = 're-entry speeds!';
    }

    // This is a weird trick to round the floats:
    unitsPerSecond = Math.round(unitsPerSecond * 100) / 100;
    metresPerSecond = Math.round(metresPerSecond * 100) / 100;
    feetPerSecond = Math.round(feetPerSecond * 100) / 100;
    kmh = Math.round(kmh * 100) / 100;
    mph = Math.round(mph * 100) / 100;
    knots = Math.round(knots * 100) / 100;
    mach = Math.round(mach * 10) / 10;

    var result = params("text_prefix").Value;

    if (params("units_xsi").Value) {
        if (result.length > 0) { result = result+"\n"; }
        result = result+unitsPerSecond.toString()+" xsi/s";
    }
    if (params("units_mPerSec").Value) {
        result = result+"\n"+metresPerSecond.toString()+" m/s";
    }
    if (params("units_ftPerSec").Value) {
        result = result+"\n"+feetPerSecond.toString()+" ft/s";
    }
    if (params("units_kmh").Value) {
        result = result+"\n"+kmh.toString()+" km/h";
    }
    if (params("units_mph").Value) {
        result = result+"\n"+mph.toString()+" mph";
    }
    if (params("units_knot").Value) {
        result = result+"\n"+knots.toString()+" knots";
    }
    if (params("units_mach").Value) {
        result = result+"\nMach "+mach.toString()+" ("+mach_txt+")";
    }

    params("moved_xsiunits").Value = dist;
    params("moved_xsiunitsPerSec").Value = dist * framerate;

    var outType = Out.Value.Type;
    if (outType === "AnnotationObject") {
        Out.Value.Parameters("Message").Value = result;
        if (params("center_bubble").Value) {
            var lines = result.split("\n");
            var longest = lines.sort(function (a, b) { return b.length - a.length; })[0];
            Out.Value.Parameters("OffsetX").Value = -params("centering_offsetPerCharacter").Value * longest.length;
        }
        else if (data.resetBubbleOffset == false) {
            Out.Value.Parameters("OffsetX").Value = 0;
            data.resetBubbleOffset = true;
        }
    }
    else if (outType === "text") {
        var separator = ", ";
        var prefix = "_RTF_{\\rtf1\\ansi\\ansicpg1252\\deff0{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\r\n\\viewkind4\\uc1\\pard\\lang1033\\fs20 ";
        var suffix = "\\par\r\n}\r\n";
        if (Out.Value.Parameters("singleline").Value === 1) {
            separator = "\\par\r\n";
        }
        Out.Value.Parameters("text").Value = prefix+result.split('\n').join(separator)+suffix;
    }
    else if (outType === 'customparamset') {
        Out.Value.Parameters(0).Value = result;
    }
    params("text_result").Value = result;

    // Update stored data for next eval:
    data.last_pos = current_pos;
    In_UpdateContext.UserData = data;

    return true;
}
'''

# =============================================================================

def XSILoadPlugin( in_reg ):
    in_reg.Author = 'Alan Fregtman'
    in_reg.Name = 'AF_Speedometer'
    in_reg.Major = 1
    in_reg.Minor = 0
    in_reg.URL = 'http://darkvertex.com'

    in_reg.RegisterCommand('GetSpeedometer', 'GetSpeedometer')
    in_reg.RegisterMenu(C.siMenuTbGetPrimitiveID, 'GetSpeedometer_Menu', False, False)
    #RegistrationInsertionPoint - do not remove this line
    return True


def XSIUnloadPlugin( in_reg ):
    Application.LogMessage('%s has been unloaded.' % in_reg.Name, C.siVerbose)
    return True

# =============================================================================

def GetSpeedometer_Init( in_ctxt ):
    oCmd = in_ctxt.Source
    oCmd.Description = 'Produces a speedometer object.'
    oCmd.ReturnValue = True

    majorVersion = xsi.Version().split('.')[0]
    defaultStyle = 'icelabel'
    if majorVersion.isdigit() and int(majorVersion) >= 11:
        defaultStyle = 'annotation'

    oArgs = oCmd.Arguments
    oArgs.AddWithHandler('inColl', 'Collection')
    oArgs.Add('style', C.siArgumentInput, defaultStyle)
    oArgs.Add('constrain', C.siArgumentInput, True)
    oArgs.Add('select', C.siArgumentInput, True)
    return True


def GetSpeedometer_Execute( inColl, style, constrain, select ):
    f = XSIFactory
    outColl = f.CreateObject('XSI.Collection')
    majorVersion = xsi.Version().split('.')[0]

    if len(inColl) == 0:
        inColl = [xsi.ActiveSceneRoot,]
        constrain = False

    for target in inColl:
        scop = f.CreateScriptedOp( 'SpeedometerOp', '', 'JScript' )
        scop.Code = scop_JS

        if style == 'annotation':
            if majorVersion.isdigit() and int(majorVersion) >= 11:
                # "Annotation Objects" were introduced in SI|2013 (aka v11.x)
                sObj = xsi.ActiveSceneRoot.AddPrimitive('AnnotationObject')
                scop.AddOutputPort(sObj.FullName+'.AnnotationObject')
            else:
                xsi.LogMessage('Annotation Objects not supported in this Softimage version. Try with SI|2013+.', 2)

        elif style == 'icelabel':
                sObj = xsi.ActiveSceneRoot.AddNull()
                sObj.primary_icon.Value = 2
                sObj.size.Value = 0.2
                subNull = sObj.AddNull('speedometer_icelabel')
                subNull.primary_icon.Value = 0
                prop = sObj.AddProperty( 'Custom_parameter_list', False, '_internals' )
                prop.AddParameter2('text', C.siString, '')
                scop.AddOutputPort(prop.FullName)
                vis = subNull.LocalProperties('Visibility')
                vis.Parameters('viewvis').AddExpression('%s.visibility.viewvis' % sObj.FullName)
                vis.Parameters('selectability').Value = False

                tree = xsi.ApplyICEOp('Set Data', subNull)
                tree.Name = 'ICE_Label'
                xsi.SetValue(tree.FullName+'.Set_Data.Reference', 'self.label')
                getDataNode = xsi.AddICENode('$XSI_DSPRESETS\\ICENodes\\GetDataNode.Preset', tree)
                xsi.SetValue(getDataNode.FullName+'.reference', 'this_parent._internals.text')
                xsi.ConnectICENodes(tree.FullName+'.Set_Data.Value', getDataNode.FullName+'.value')
                xsi.DisplayPortValues(tree.FullName+'.Set_Data.Value', True, 0, True, '', 0, 0, 3, 1, False, True, 1, 1, 1, 1, False, 0, 10000, 1, False, False, 0, 10, False, True, False, 100)

        elif style == 'text':
            sObj = xsi.CreatePrim('Text', 'NurbsCurve')
            scop.AddOutputPort(sObj.FullName+'.crvlist.TextToCurveList.text')
            tPrim = sObj.Primitives(0)  # because sObj.ActivePrimitive returns 'crvlist', not 'text'.
            tPrim.Parameters('singleline').Value = 0
            tPrim.Parameters('use_ratio').Value = 1
            tPrim.Parameters('ratio').Value = 5

        scop.AddInputPort(sObj.FullName+'.kine.global')

        txtPrefix = scop.AddParameter( f.CreateParamDef2('text_prefix', C.siString, '') )
        fr = scop.AddParameter( f.CreateParamDef2('framerate', C.siDouble, 24.0, 1.0, 1000.0) )
        scop.AddParameter( f.CreateParamDef2('one_metre_equals', C.siDouble, 10.0, 0.001, 1000.0) )
        scop.AddParameter( f.CreateParamDef2('units_xsi', C.siBool, True) )
        scop.AddParameter( f.CreateParamDef2('units_mPerSec', C.siBool, False) )
        scop.AddParameter( f.CreateParamDef2('units_ftPerSec', C.siBool, False) )
        scop.AddParameter( f.CreateParamDef2('units_kmh', C.siBool, True) )
        scop.AddParameter( f.CreateParamDef2('units_mph', C.siBool, True) )
        scop.AddParameter( f.CreateParamDef2('units_knot', C.siBool, False) )
        scop.AddParameter( f.CreateParamDef2('units_mach', C.siBool, False) )
        scop.AddParameter( f.CreateParamDef2('center_bubble', C.siBool, True) )
        scop.AddParameter( f.CreateParamDef2('centering_offsetPerCharacter', C.siDouble, 8.0, 0.0, 20.0) )
        scop.AddParameter( f.CreateParamDef2('moved_xsiunits', C.siDouble, 0.0, 0.0, 1000000.0) )
        scop.AddParameter( f.CreateParamDef2('moved_xsiunitsPerSec', C.siDouble, 0.0, 0.0, 1000000.0) )
        scop.AddParameter( f.CreateParamDef2('text_result', C.siString, '') )

        scop.AlwaysEvaluate = True
        scop.Debug = 0
        scop.Connect()
        fr.AddExpression('Fr')
        outColl.AddItems(sObj)
        sObj.Name = 'speedometer'

        if constrain:

            if target.Type.endswith('SubComponent'):
                if target.Type.startswith('pnt'):
                    clsType = C.siVertexCluster
                elif target.Type.startswith('poly'):
                    clsType = C.siPolygonCluster
                indices = target.SubComponent.ComponentCollection.IndexArray
                target = target.SubComponent.Parent3DObject
                newCluster = target.ActivePrimitive.Geometry.AddCluster( clsType, 'speedometer', indices )
                sObj.Kinematics.AddConstraint('ObjectToCluster', newCluster)
            else:
                cnsComp = False
                if target.Type in ['polymsh','surfmsh']:
                    # Offset onto top of target mesh by raycasting upwards from its bbox center:

                    geo = target.ActivePrimitive.Geometry
                    xform = target.Kinematics.Global.Transform
                    position = geo.GetBoundingBox()[:3]
                    direction = [0,1,0]  # +Y

                    pointLocator = geo.GetRaycastIntersections(position, direction)
                    p = geo.EvaluatePositions(pointLocator)
                    newPos = XSIMath.CreateVector3(p[0][0], p[1][0], p[2][0])
                    newPos.MulByTransformationInPlace(xform)
                    xform.SetTranslation(newPos)

                    sObj.Kinematics.Global.Transform = xform
                    cnsComp = True

                sObj.Kinematics.AddConstraint('Pose', target, cnsComp)

            txtPrefix.Value = '%s:\n\n' % (target.FullName if target.Model.Name.startswith('Scene_Root') else target.Model.Name)


        # Add DisplayInfo property:
        prop = sObj.AddProperty( 'Custom_parameter_list', False, 'DisplayInfo_options' )
        prop.AddProxyParameter( '%s.text_prefix' % scop.FullName, 'text_prefix', 'Title:' )
        prop.AddProxyParameter( '%s.one_metre_equals' % scop.FullName, 'one_metre_equals', '1m equals:' )
        prop.AddProxyParameter( '%s.units_xsi' % scop.FullName, 'units_xsi', 'Units: XSI/s' )
        prop.AddProxyParameter( '%s.units_mPerSec' % scop.FullName, 'units_mPerSec', 'Units: m/s' )
        prop.AddProxyParameter( '%s.units_ftPerSec' % scop.FullName, 'units_ftPerSec', 'Units: ft/s' )
        prop.AddProxyParameter( '%s.units_kmh' % scop.FullName, 'units_kmh', 'Units: kmh' )
        prop.AddProxyParameter( '%s.units_mph' % scop.FullName, 'units_mph', 'Units: mph' )
        prop.AddProxyParameter( '%s.units_knot' % scop.FullName, 'units_knot', 'Units: knots' )
        prop.AddProxyParameter( '%s.units_mach' % scop.FullName, 'units_mach', 'Units: Mach' )
        if style == 'annotation':
            prop.AddProxyParameter( '%s.center_bubble' % scop.FullName, 'center_bubble', 'Center:' )
            prop.AddProxyParameter( '%s.centering_offsetPerCharacter' % scop.FullName, 'centering_offsetPerCharacter', 'Ctr. Factor:' )
            prop.AddProxyParameter( '%s.AnnotationObject.R' % sObj.FullName, 'color_r', 'Color R:' )
            prop.AddProxyParameter( '%s.AnnotationObject.G' % sObj.FullName, 'color_g', 'Color G:' )
            prop.AddProxyParameter( '%s.AnnotationObject.B' % sObj.FullName, 'color_b', 'Color B:' )
            prop.AddProxyParameter( '%s.AnnotationObject.DistanceFading' % sObj.FullName, 'distance_fading', 'Fade If Far:' )
        xsi.SetKeyableAttributes(sObj.FullName+'.DisplayInfo_options', 'DisplayInfo_options.{one_metre_equals,units_ftPerSec,units_kmh,units_knot,units_mPerSec,units_mach,units_mph,units_xsi}', 'siKeyableAttributeKeyable')


    if select and not constrain:
        xsi.SelectObj(outColl)

    return outColl


def GetSpeedometer_Menu_Init( in_ctxt ):
    oMenu = in_ctxt.Source
    oMenu.AddCommandItem('Speedometer', 'GetSpeedometer')
    return True
