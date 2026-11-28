# -*- coding: utf-8 -*-
"""skinning_tools_qt

A tool for various skinning tasks in Maya.

created by gadget-design T.Kondo (http://www.gadget-design.com)

Files:
  skinning_tools_qt consists of the following 3 files.
     skinning_tools_qt.py                This Python script
     skinning_tools_qt_manual_Eng.html   Manual (English)
     skinning_tools_qt_manual_Jpn.html   Manual (Japanese)

     Place skinning_tools_qt_manual_Eng(_Jpn).html in the same folder as skinning_tools_qt.py.

Usage:
  Run the following in the Python tab of Maya's Script Editor.
  Replace path with the location of skinning_tools_qt.py.

    path = r"C:/tools/skinning_tools_qt.py"
    with open(path, encoding="utf-8") as f:
        exec(compile(f.read(), path, "exec"))

  If you put the file in a scripts folder and import it, call main() as follows.
    import skinning_tools_qt
    skinning_tools_qt.main()

"""

import os
import re

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import isValid, wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import isValid, wrapInstance

QActionGroup = getattr( QtGui, "QActionGroup", None ) or QtWidgets.QActionGroup


_MAIN_WIN = "skinningToolsQtUI"
_TOOL_NAME = "skinning_tools_qt"
_MANUALS = [("Manual (English)", "skinning_tools_qt_manual_Eng.html"),
            ("Manual (Japanese)", "skinning_tools_qt_manual_Jpn.html")]
_MANUAL_WIN = "skinningToolsQtManual"
_VERSION = "1.0.6"
_AUTHOR = "gadget-design T.Kondo"
_AUTHOR_URL = "http://www.gadget-design.com"
_UPDATE_URL = "https://github.com/gadget-design/skinning_tools_qt"

_BLOCK_MARGIN_W = 5
_BLOCK_MARGIN_H = 5
_PSW_LOWER_BG_COLOR = (0.2, 0.2, 0.2)
_PSW_LOWER_PAD = 5
_SPLITTER_GAP = 7
_SPLITTER_BAND_H = 6
_SPLITTER_BAND_COLOR = (0.37, 0.37, 0.45)
_SPLITTER_DOT_COLOR = (0.92, 0.92, 0.92)
_SPLITTER_DOT_W = 2
_PANE_TOP_PCT = 50
_WIN_SIZE = (495, 1000)

_WT_MIN_HEIGHT = 80
_WT_CELL_W = 44
_WT_CELL_H = 20
_WT_HEAD_TEXT_H = 50
_WT_NAME_MAX_CHARS = 30
_WT_LOCK_H = 24
_WT_MAX_ROWS = 1000
_WT_EPS = 1e-6
_DESELECT_DELAY_MS = 250
_SW_PRESET_W = 46
_SW_PRESET_H = 30
_SW_PRESET_GAP = 15
_WT_INF_COLOR = (0.55, 0.38, 0.18)
_WT_INF_SEL_COLOR = (0.85, 0.6, 0.25)
_WT_INF_LOCK_TEXT_COLOR = (0.65, 0.65, 0.65)
_WT_INF_LOCK_SEL_TEXT_COLOR = (0.35, 0.3, 0.25)
_WT_INF_CELL_COLOR = (0.18, 0.34, 0.5)
_WT_INF_CELL_SEL_COLOR = (0.35, 0.62, 0.85)
_WT_INF_CELL_LOCK_SEL_TEXT_COLOR = (0.22, 0.3, 0.38)
_WT_INF_EXTRA_COLOR = (0.4, 0.4, 0.4)
_WT_INF_EXTRA_SEL_COLOR = (0.4, 0.4, 0.4)
_WT_INF_EXTRA_LOCK_SEL_TEXT_COLOR = (0.38, 0.38, 0.38)
_WT_VTX_COLOR = (0.36, 0.36, 0.36)
_WT_BG_COLOR = (0.169, 0.169, 0.169)
_WT_HEAD_BG_COLOR = (0.25, 0.25, 0.25)
_WT_CELL_SEL_COLOR = (0.3, 0.55, 0.75)
_WT_STATUS_COLOR = (1.0, 1.0, 1.0)
_WT_STATUS_VTX_COLOR = (0.9, 0.85, 0.2)
_WT_STATUS_CELL_COLOR = (0.3, 0.75, 1.0)
_WT_CELL_LOCK_COLOR = (0.3, 0.3, 0.3)
_WT_CELL_LOCK_TEXT_COLOR = (0.6, 0.6, 0.6)
_VTX_RANGE = re.compile( r"vtx\[(\d+)(?::(\d+))?\]$" )

_LOCK_ON_ICON = ":/Lock_ON.png"
_LOCK_OFF_ICON = ":/Lock_OFF_grey.png"
_LOCKED_INF_TEXT_COLOR = (0.5, 0.5, 0.5)
_LOCKED_INF_SEL_TEXT_COLOR = (0.7, 0.7, 0.7)

_SW_PRESETS = [
    ("+0.001", 0.001, (0.55, 0.5, 0.5)), ("+0.01", 0.01, (0.6, 0.5, 0.5)),
    ("+0.05", 0.05, (0.7, 0.5, 0.5)), ("+0.10", 0.10, (0.8, 0.5, 0.5)),
    ("-0.001", -0.001, (0.5, 0.5, 0.55)), ("-0.01", -0.01, (0.5, 0.5, 0.6)),
    ("-0.05", -0.05, (0.5, 0.5, 0.7)), ("-0.10", -0.10, (0.5, 0.5, 0.8)),
]

_PAINT_PRESETS = [
    ("+0.01", "add", 0.01, (0.6, 0.2, 0.2), 40), ("+0.02", "add", 0.02, (0.65, 0.2, 0.2), 40),
    ("+0.10", "add", 0.10, (0.7, 0.2, 0.2), 40), ("+0.20", "add", 0.20, (0.8, 0.2, 0.2), 40),
    ("x0.80", "scl", 0.80, (0.2, 0.2, 0.9), 40), ("x0.90", "scl", 0.90, (0.2, 0.2, 0.85), 40),
    ("x0.98", "scl", 0.98, (0.2, 0.2, 0.65), 40), ("x0.99", "scl", 0.99, (0.2, 0.2, 0.6), 40),
]

_BRUSHES = [("gaussian", ":/circleGaus.png", "G"), ("poly", ":/circlePoly.png", "P"),
            ("solid", ":/circleSolid.png", "S")]
_BRUSH_TIPS = {"gaussian": "Brush shape: Gaussian.", "poly": "Brush shape: Poly.", "solid": "Brush shape: Solid."}

_OPERATIONS = [("Replace", "absolute"), ("Add", "additive"), ("Scale", "scale"), ("Smooth", "smooth")]
_OPERATION_TIPS = {"Replace": "Paint operation: replace the weights with Val.",
                   "Add": "Paint operation: add Val to the weights.",
                   "Scale": "Paint operation: multiply the weights by Val.",
                   "Smooth": "Paint operation: smooth the weights."}

_TOOLTIP_STYLE = ("QToolTip { color: black; background-color: rgb(255, 255, 220); "
                  "border: 1px solid rgb(118, 118, 118); }")

_LANG_OPTVAR = "ST_UILang"
_LANGS = [("en", "English"), ("ja", "Japanese")]
_lang = ["ja"]

_JA = {
    "Edit": u"編集",
    "Auto Load Object": u"選択オブジェクトを自動で読み込む",
    "Load Selected Object": u"選択オブジェクトを読み込む",
    "List": u"リスト",
    "Alphabetical": u"名前順",
    "Reverse Alphabetical": u"名前順 (逆順)",
    "Graph Order": u"グラフ順",
    "Reverse Graph Order": u"グラフ順 (逆順)",
    "Hold": u"ロック中をリスト後ろへ",
    "Reverse Hold": u"ロック中をリスト前へ",
    "Tools": u"ツール",
    "Select Affected Points": u"影響ポイントを選択",
    "Remove Unused Influences": u"未使用インフルエンスの除去",
    "Add/Remove Influences": u"インフルエンスの追加 / 除去",
    "Add Influences": u"インフルエンスの追加",
    "Remove Influences": u"インフルエンスの除去",
    "Language": u"言語 (Language)",
    "Help": u"ヘルプ",
    "Manual (Japanese)": u"マニュアル (日本語)",
    "Manual (English)": u"マニュアル (英語)",
    "Manual not found: {}": u"マニュアルが見つかりません: {}",
    "About  {}": u"{} について",
    "Update": u"アップデート",
    "The latest version is available here:": u"最新版はこちらから入手できます:",
    "Paint Skin Weights": u"スキンウェイトのペイント",
    "Start Paint Mode": u"ペイントモード開始",
    "End Paint Mode": u"ペイントモード終了",
    "Enter the Paint Skin Weights tool.": u"スキンウェイトペイントツールに入る",
    "Exit the Paint Skin Weights tool.": u"スキンウェイトペイントツールを終了する",
    "Lock All": u"全てロック",
    "Unlock All": u"全てアンロック",
    "Lock the weights of all influences.": u"全てのインフルエンスのウェイトをロックする",
    "Unlock the weights of all influences.": u"全てのインフルエンスのウェイトをアンロックする",
    "Skin Cluster:": u"スキンクラスター:",
    "Skin cluster name. Right-click to select the skin cluster node or its geometry.":
        u"スキンクラスター名: 右クリックでスキンクラスターの選択 または ジオメトリの選択",
    "Select Skin Cluster Node": u"スキンクラスターノードを選択",
    "Select Geometry": u"ジオメトリを選択",
    " (Lock)": u" (ロック)",
    "Lock / unlock the weights of {}.": u"{} のウェイトをロック / アンロックする",
    "Replace": u"置き換え",
    "Add": u"追加",
    "Scale": u"スケール",
    "Smooth": u"スムーズ",
    "Color or Mono": u"カラー / 白黒",
    "Brush shape: Gaussian.": u"ブラシの形状: ガウス",
    "Brush shape: Poly.": u"ブラシの形状: ポリゴン",
    "Brush shape: Solid.": u"ブラシの形状: ソリッド",
    "Paint operation: replace the weights with Val.": u"ペイント操作: ウェイトを 値 で置き換える",
    "Paint operation: add Val to the weights.": u"ペイント操作: ウェイトに 値 を加算する",
    "Paint operation: multiply the weights by Val.": u"ペイント操作: ウェイトに 値 を乗算する",
    "Paint operation: smooth the weights.": u"ペイント操作: ウェイトをスムーズにする",
    "Switch the weight display in paint mode between color and grayscale.":
        u"ペイントモードのウェイトの表示を、カラーと白黒で切り替える",
    "Set the paint operation to Add and Val to {}.": u"ペイント操作を 追加、値を {} にする",
    "Set the paint operation to Scale and Val to {}.": u"ペイント操作を スケール、値を {} にする",
    "Opac": u"不透明度",
    "Val": u"値",
    "Flood": u"塗りつぶす",
    "Flood the whole geometry with the current settings (Opac, Val) for the selected influence.":
        u"選択中のインフルエンスに、現在の設定値(Opac,Val)で、ジオメトリ全体を塗りつぶすウェイトを設定します。",
    "Preset : ": u"プリセット : ",
    "add": u"加算",
    "scale": u"乗算",
    "Hold/Unhold": u"ロック / アンロック",
    "Hold All": u"全てロック",
    "Unhold All": u"全てアンロック",
    "Select Influence": u"インフルエンスを選択",
    "Select Influences": u"インフルエンスを選択",
    "Select affected points": u"影響を受けるポイントを選択",
    "Reveal selected influence": u"選択中のインフルエンスをリストで選択",
    "Set Vertex Weights:": u"頂点ウェイトの設定:",
    "Start Component Mode": u"コンポーネントモード開始",
    "End Component Mode": u"コンポーネントモード終了",
    "Enter component mode.": u"コンポーネントモードに入る",
    "Return to object mode.": u"オブジェクトモードに戻る",
    "Add:": u"加算:",
    "Sub:": u"減算:",
    "Add {} to the weights of the selected influences on the selected vertices. "
    "When cells of the table are selected, add it to the cells.":
        u"選択中の頂点の、選択中のインフルエンスのウェイトに {} を加算する。"
        u"表のセルを選択しているときは、そのセルに加算する",
    "Subtract {} from the weights of the selected influences on the selected vertices. "
    "When cells of the table are selected, subtract it from the cells.":
        u"選択中の頂点の、選択中のインフルエンスのウェイトから {} を減算する。"
        u"表のセルを選択しているときは、そのセルから減算する",
    "Click to collapse / expand.": u"クリックで折りたたみ / 展開する",
    "Close this dialog.": u"このダイアログを閉じる",
    "Status: ": u"ステータス：",
    "Status: Vertex mode": u"ステータス：バーテックス モード",
    "Status: Cell mode": u"ステータス：セル モード",
    "Copy": u"コピー",
    "Paste": u"ペースト",
    "Copy the weights of the selected vertices, in the order they were selected. "
    "When cells of the table are selected, copy the cell values in the order they were selected.":
        u"選択した頂点のウェイトを、選択した順にコピーする。"
        u"表のセルを選択しているときは、セルの値を選択した順にコピーする",
    "Paste the copied weights to the selected vertices, in the order they were selected "
    "(if one vertex was copied, to all of them). When cells of the table are selected, "
    "paste the copied cell values to them in the same way. Locked influences are unlocked automatically.":
        u"コピーしたウェイトを、選択した頂点に選択した順にペーストする (1 頂点だけコピーしたときは"
        u"選択した全部の頂点に)。表のセルを選択しているときは、コピーしたセルの値を同じようにペーストする。"
        u"ロック中のインフルエンスは自動でアンロックする",
    "Select vertices one by one in order and try again.":
        u"頂点を 1 つずつ順に選択してから、もう一度やり直してください。",
    "{} has no skinCluster.": u"{} にスキンクラスターがありません。",
    "Copied the weights of {} vertices.": u"{} 個の頂点のウェイトをコピーしました。",
    "Copy the weights first.": u"先にウェイトをコピーしてください。",
    "Copied {} vertices but {} are selected. Pasted to the first {}.":
        u"コピーした頂点は {} 個ですが、{} 個選択されています。先頭の {} 個にペーストしました。",
    "{} does not have these influences: {}": u"{} に次のインフルエンスがありません: {}",
    "Unlocked influences: {}": u"アンロックしたインフルエンス: {}",
    "Pasted the weights to {} vertices.": u"{} 個の頂点にウェイトをペーストしました。",
    "Copied {} cell values.": u"{} 個のセルの値をコピーしました。",
    "Copy the cell values first.": u"先にセルの値をコピーしてください。",
    "Copied {} cells but {} are selected. Pasted to the first {}.":
        u"コピーしたセルは {} 個ですが、{} 個選択されています。先頭の {} 個にペーストしました。",
    "Pasted the values to {} cells.": u"{} 個のセルに値をペーストしました。",
    "Close": u"閉じる",
    "Close SkinningTools Window": u"skinningTools ウィンドウを閉じる",
    "Remove Influence": u"インフルエンスの除去",
    "Remove influence {} from {}?": u"{1} から {0} を除去しますか?",
    "Remove influences from {}?": u"{} から選択中のインフルエンスを除去しますか?",
    "Yes": u"はい",
    "No": u"いいえ",
    "Selected object has multiple shapes. This can produce undesirable results.":
        u"選択オブジェクトに複数のシェイプがあります。意図しない結果になることがあります。",
    "Skin cluster specified incorrectly. Try again.":
        u"スキンクラスターの指定が正しくありません。もう一度やり直してください。",
    'Set does not belong to current skinCluster. Try again or use "Complete Set".':
        u'セットが今のスキンクラスターのものではありません。やり直すか "Complete Set" を使ってください。',
    "Select some points and try again.": u"ポイントを選択してから、もう一度やり直してください。",
    "Select one or more influences from the UI list and try again.":
        u"リストでインフルエンスを 1 つ以上選択してから、もう一度やり直してください。",
    "Selected object is not loaded into UI. Try again.":
        u"選択オブジェクトがツールに読み込まれていません。もう一度やり直してください。",
    'Influence {} is locked. Toggle "Hold" off and try again.':
        u"インフルエンス {} はロック中です。アンロックしてから、もう一度やり直してください。",
    "Weight table: showing the first {} of {} points.": u"ウェイト表: {1} 個のポイントのうち、先頭の {0} 個を表示しています。",
    "Weight table: showing the first {} selected points.": u"ウェイト表: 選択中のポイントのうち、先頭の {} 個を表示しています。",
    "The selected cells are locked. Unlock the influences and try again.":
        u"選択中のセルはロック中です。インフルエンスをアンロックしてから、もう一度やり直してください。",
    "No influences selected.": u"インフルエンスが選択されていません。",
    "No influences selected. Try again.": u"インフルエンスが選択されていません。もう一度やり直してください。",
    "{} is already part of {}. Ignoring.": u"{} は既に {} のインフルエンスです。スキップします。",
    "Given skinCluster node is incorrect. Try again.":
        u"スキンクラスターノードが正しくありません。もう一度やり直してください。",
    "Finding skinCluster points...": u"スキンクラスターのポイントを検索中...",
    "{} is not an influence of {}.": u"{} は {} のインフルエンスではありません。",
    "Not in paint mode. Press Start Paint Mode before Flood.":
        u"ペイントモードではありません。ペイントモード開始 を押してから フラッド してください",
    "Select an influence.": u"インフルエンスを選択してください",
}


def _tr( text ):
    if _lang[0] == "ja":
        return _JA.get( text, text )
    return text


def _load_lang():
    lang = cmds.optionVar( q=_LANG_OPTVAR ) if cmds.optionVar( ex=_LANG_OPTVAR ) else "ja"
    _lang[0] = lang if lang in dict( _LANGS ) else "ja"


_win = [None]
_wt_grid = {"skin": "", "verts": [], "infs": [], "extra": []}
_wt_anchor = [None]
_cm_tgl = [0]
_lock_cache = {}


def _maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( int( ptr ), QtWidgets.QWidget ) if ptr else None


def _rgb( color ):
    return "rgb(%d, %d, %d)" % tuple( int( c * 255 ) for c in color )


def _qcolor( color ):
    return QtGui.QColor( *[int( c * 255 ) for c in color] )


def _event_pos( event ):
    if hasattr( event, "position" ):
        return event.position().toPoint()
    return event.pos()


def _color_button( label, color, w=None, h=24, tip="" ):
    btn = QtWidgets.QPushButton( label )
    btn.setStyleSheet(
        "QPushButton { background-color: %s; border: 1px solid rgb(40, 40, 40); "
        "border-radius: 2px; padding: 0px 2px; }"
        "QPushButton:hover { border-color: rgb(170, 170, 170); }"
        "QPushButton:pressed { background-color: rgb(60, 60, 60); }" % _rgb( color ))
    if w:
        btn.setFixedWidth( w )
    btn.setFixedHeight( h )
    if tip:
        btn.setToolTip( tip )
    return btn


def _lock_pixmap( on ):
    on = bool( on )
    if on not in _lock_cache:
        _lock_cache[on] = _make_lock_pixmap( on )
    return _lock_cache[on]


def _make_lock_pixmap( on ):
    pix = QtGui.QPixmap( _LOCK_ON_ICON if on else _LOCK_OFF_ICON )
    if not pix.isNull():
        return pix
    pix = QtGui.QPixmap( 16, 16 )
    pix.fill( QtGui.QColor( 0, 0, 0, 0 ) )
    painter = QtGui.QPainter( pix )
    painter.setRenderHint( QtGui.QPainter.RenderHint.Antialiasing )
    color = QtGui.QColor( 235, 200, 80 ) if on else QtGui.QColor( 150, 150, 150 )
    painter.setPen( QtGui.QPen( color, 1.6 ) )
    painter.setBrush( QtCore.Qt.BrushStyle.NoBrush )
    painter.drawArc( QtCore.QRectF( 4.5, 1.5, 7, 9 ) if on else QtCore.QRectF( 8.5, 0.5, 7, 9 ), 0, 180 * 16 )
    painter.setPen( QtCore.Qt.PenStyle.NoPen )
    painter.setBrush( color )
    painter.drawRoundedRect( QtCore.QRectF( 3, 7, 10, 8 ), 1.5, 1.5 )
    painter.end()
    return pix


class _FlowLayout( QtWidgets.QLayout ):

    def __init__( self, parent=None, spacing=2 ):
        super( _FlowLayout, self ).__init__( parent )
        self._items = []
        self._space = spacing
        self.setContentsMargins( 0, 0, 0, 0 )

    def addItem( self, item ):
        self._items.append( item )

    def count( self ):
        return len( self._items )

    def itemAt( self, index ):
        return self._items[index] if 0 <= index < len( self._items ) else None

    def takeAt( self, index ):
        return self._items.pop( index ) if 0 <= index < len( self._items ) else None

    def expandingDirections( self ):
        return QtCore.Qt.Orientation( 0 )

    def hasHeightForWidth( self ):
        return True

    def heightForWidth( self, width ):
        return self._arrange( QtCore.QRect( 0, 0, width, 0 ), True )

    def setGeometry( self, rect ):
        super( _FlowLayout, self ).setGeometry( rect )
        self._arrange( rect, False )

    def sizeHint( self ):
        return self.minimumSize()

    def minimumSize( self ):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo( item.minimumSize() )
        m = self.contentsMargins()
        return size + QtCore.QSize( m.left() + m.right(), m.top() + m.bottom() )

    def _arrange( self, rect, test_only ):
        m = self.contentsMargins()
        area = rect.adjusted( m.left(), m.top(), -m.right(), -m.bottom() )
        x = area.x()
        y = area.y()
        line_h = 0
        for item in self._items:
            hint = item.sizeHint()
            if x + hint.width() > area.right() + 1 and line_h > 0:
                x = area.x()
                y += line_h + self._space
                line_h = 0
            if not test_only:
                item.setGeometry( QtCore.QRect( QtCore.QPoint( x, y ), hint ) )
            x += hint.width() + self._space
            line_h = max( line_h, hint.height() )
        return y + line_h - rect.y() + m.bottom()


def _flow_widget( spacing=2 ):
    widget = QtWidgets.QWidget()
    layout = _FlowLayout( widget, spacing )
    return widget, layout


def _add_preset_label( flow, text, gap=0, h=24 ):
    if gap:
        spacer = QtWidgets.QWidget()
        spacer.setFixedSize( gap, 1 )
        flow.addWidget( spacer )
    label = QtWidgets.QLabel( text )
    label.setFixedHeight( h )
    label.setAlignment( QtCore.Qt.AlignmentFlag.AlignVCenter )
    flow.addWidget( label )


class _FloatSliderGrp( QtWidgets.QWidget ):

    changed = QtCore.Signal( float )

    def __init__( self, label, value, min_v, max_v, field_min, field_max, precision,
                  label_w=42, field_w=38, parent=None ):
        super( _FloatSliderGrp, self ).__init__( parent )
        self._min = min_v
        self._max = max_v
        self._steps = 1000
        self._last = None
        layout = QtWidgets.QHBoxLayout( self )
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.setSpacing( 4 )
        text = QtWidgets.QLabel( label )
        text.setFixedWidth( label_w )
        self.field = QtWidgets.QDoubleSpinBox()
        self.field.setButtonSymbols( QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons )
        self.field.setRange( field_min, field_max )
        self.field.setDecimals( precision )
        self.field.setFixedWidth( field_w )
        self.slider = QtWidgets.QSlider( QtCore.Qt.Orientation.Horizontal )
        self.slider.setRange( 0, self._steps )
        layout.addWidget( text )
        layout.addWidget( self.field )
        layout.addWidget( self.slider, 1 )
        self.setValue( value )
        self.slider.valueChanged.connect( self._slider_moved )
        self.slider.sliderReleased.connect( self._emit )
        self.field.editingFinished.connect( self._field_edited )

    def value( self ):
        return self.field.value()

    def setValue( self, value ):
        self.field.blockSignals( True )
        self.slider.blockSignals( True )
        self.field.setValue( value )
        ratio = ( min( max( value, self._min ), self._max ) - self._min ) / float( self._max - self._min )
        self.slider.setValue( int( round( ratio * self._steps ) ) )
        self.field.blockSignals( False )
        self.slider.blockSignals( False )
        self._last = self.field.value()

    def _slider_moved( self, pos ):
        self.field.blockSignals( True )
        self.field.setValue( self._min + ( self._max - self._min ) * pos / float( self._steps ) )
        self.field.blockSignals( False )
        if not self.slider.isSliderDown():
            self._emit()

    def _field_edited( self ):
        value = self.field.value()
        last = self._last
        self.setValue( value )
        self._last = last
        self._emit()

    def _emit( self ):
        if self.value() == self._last:
            return
        self._last = self.value()
        self.changed.emit( self._last )


class _CollapsibleFrame( QtWidgets.QWidget ):

    toggled = QtCore.Signal( bool )

    def __init__( self, title, parent=None ):
        super( _CollapsibleFrame, self ).__init__( parent )
        self.header = QtWidgets.QToolButton()
        self.header.setText( title )
        self.header.setCheckable( True )
        self.header.setChecked( True )
        self.header.setArrowType( QtCore.Qt.ArrowType.DownArrow )
        self.header.setToolButtonStyle( QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon )
        self.header.setSizePolicy( QtWidgets.QSizePolicy.Policy.Expanding,
                                   QtWidgets.QSizePolicy.Policy.Fixed )
        self.header.setFixedHeight( 22 )
        self.header.setToolTip( _tr( "Click to collapse / expand." ) )
        self.header.setStyleSheet(
            "QToolButton { background-color: rgb(93, 93, 93); border: none; "
            "font-weight: bold; padding-left: 4px; text-align: left; }")
        self.header.clicked.connect( self._clicked )
        self.body = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout( self.body )
        self.body_layout.setContentsMargins( _BLOCK_MARGIN_W, _BLOCK_MARGIN_H,
                                             _BLOCK_MARGIN_W, _BLOCK_MARGIN_H )
        self.body_layout.setSpacing( 4 )
        layout = QtWidgets.QVBoxLayout( self )
        layout.setContentsMargins( 0, 0, 0, 0 )
        layout.setSpacing( 0 )
        layout.addWidget( self.header )
        layout.addWidget( self.body, 1 )

    def header_height( self ):
        return self.header.height()

    def _clicked( self, expanded ):
        self.body.setVisible( expanded )
        self.header.setArrowType( QtCore.Qt.ArrowType.DownArrow if expanded
                                  else QtCore.Qt.ArrowType.RightArrow )
        self.toggled.emit( not expanded )


class _SplitterHandle( QtWidgets.QSplitterHandle ):

    def paintEvent( self, event ):
        painter = QtGui.QPainter( self )
        y = self.height() // 2
        top = y - _SPLITTER_BAND_H // 2
        painter.fillRect( 0, top, self.width(), _SPLITTER_BAND_H, _qcolor( _SPLITTER_BAND_COLOR ) )
        pen = QtGui.QPen( _qcolor( _SPLITTER_DOT_COLOR ) )
        pen.setWidth( _SPLITTER_DOT_W )
        pen.setStyle( QtCore.Qt.PenStyle.DotLine )
        pen.setCapStyle( QtCore.Qt.PenCapStyle.FlatCap )
        painter.setPen( pen )
        painter.drawLine( int( self.width() * 0.35 ), y, int( self.width() * 0.65 ), y )
        painter.end()


class _Splitter( QtWidgets.QSplitter ):
    def createHandle( self ):
        return _SplitterHandle( self.orientation(), self )


class _InfluenceDelegate( QtWidgets.QStyledItemDelegate ):

    def initStyleOption( self, option, index ):
        super( _InfluenceDelegate, self ).initStyleOption( option, index )
        if index.data( QtCore.Qt.ItemDataRole.UserRole ):
            option.text = option.text + _tr( " (Lock)" )
            option.palette.setColor( QtGui.QPalette.ColorRole.HighlightedText,
                                     _qcolor( _LOCKED_INF_SEL_TEXT_COLOR ) )


class _InfluenceTree( QtWidgets.QTreeWidget ):

    lock_pressed = QtCore.Signal( str )
    lock_dragged = QtCore.Signal( str, str )
    lock_drag_finished = QtCore.Signal()

    def __init__( self, parent=None ):
        super( _InfluenceTree, self ).__init__( parent )
        self.setColumnCount( 2 )
        self.setHeaderHidden( True )
        self.setRootIsDecorated( False )
        self.setIndentation( 0 )
        self.setUniformRowHeights( True )
        self.setSelectionMode( QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection )
        self.setIconSize( QtCore.QSize( 16, 16 ) )
        self.header().setStretchLastSection( True )
        self.setColumnWidth( 0, 26 )
        self.setContextMenuPolicy( QtCore.Qt.ContextMenuPolicy.CustomContextMenu )
        self.setItemDelegate( _InfluenceDelegate( self ) )
        self._collapse_timer = QtCore.QTimer( self )
        self._collapse_timer.setSingleShot( True )
        self._collapse_timer.timeout.connect( self._apply_collapse )
        self._collapse_to = None
        self._collapse_deselect = False
        self._just_deselected = None
        self._defer_item = None
        self._press_pos = QtCore.QPoint()

    def _lock_column_item( self, event ):
        index = self.indexAt( _event_pos( event ) )
        if index.isValid() and index.column() == 0:
            return self.itemFromIndex( index )
        return None

    def mousePressEvent( self, event ):
        item = self._lock_column_item( event )
        if item is not None and event.button() == QtCore.Qt.MouseButton.LeftButton:
            if not item.icon( 0 ).isNull():
                self.lock_pressed.emit( item.text( 1 ) )
                self._start_lock_drag( item )
            self._lock_down = True
            return
        self._collapse_timer.stop()
        self._collapse_to = None
        self._just_deselected = None
        selected = self.selectedItems()
        self.press_selection = [it.text( 1 ) for it in selected]
        item = self.itemAt( _event_pos( event ) )
        self._defer_item = None
        if ( event.button() == QtCore.Qt.MouseButton.LeftButton
                and event.modifiers() == QtCore.Qt.KeyboardModifier.NoModifier
                and item is not None and item.isSelected() ):
            self._defer_item = item
            self._collapse_deselect = len( selected ) == 1
            self._press_pos = _event_pos( event )
        super( _InfluenceTree, self ).mousePressEvent( event )

    _lock_down = False
    press_selection = []

    _lock_drag_source = None
    _lock_drag_row = -1

    def _start_lock_drag( self, item ):
        self._lock_drag_source = item
        self._lock_drag_row = self.indexOfTopLevelItem( item )

    def _drag_lock_to( self, pos ):
        source = self._lock_drag_source
        item = self.itemAt( QtCore.QPoint( 0, pos.y() ) )
        if source is None or item is None:
            return
        row = self.indexOfTopLevelItem( item )
        last = self._lock_drag_row
        if row == last or row < 0:
            return
        step = 1 if row > last else -1
        for r in range( last + step, row + step, step ):
            target = self.topLevelItem( r )
            if target is not None and target is not source and not target.icon( 0 ).isNull():
                self.lock_dragged.emit( source.text( 1 ), target.text( 1 ) )
        self._lock_drag_row = row
        self.scrollToItem( item )

    def mouseMoveEvent( self, event ):
        if self._lock_down:
            if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
                self._drag_lock_to( _event_pos( event ) )
            return
        if ( self._defer_item is not None and event.buttons() & QtCore.Qt.MouseButton.LeftButton
                and ( _event_pos( event ) - self._press_pos ).manhattanLength()
                >= QtWidgets.QApplication.startDragDistance() ):
            self._defer_item = None
        super( _InfluenceTree, self ).mouseMoveEvent( event )

    def mouseReleaseEvent( self, event ):
        if self._lock_down:
            self._lock_down = False
            if self._lock_drag_source is not None:
                self.lock_drag_finished.emit()
            self._lock_drag_source = None
            return
        item = self._defer_item
        self._defer_item = None
        if item is None or self.itemAt( _event_pos( event ) ) is not item:
            super( _InfluenceTree, self ).mouseReleaseEvent( event )
            return
        keep = self.selectedItems()
        self.blockSignals( True )
        try:
            super( _InfluenceTree, self ).mouseReleaseEvent( event )
            for it in keep:
                it.setSelected( True )
        finally:
            self.blockSignals( False )
        self._collapse_to = item
        delay = QtWidgets.QApplication.doubleClickInterval()
        if self._collapse_deselect:
            delay = min( delay, _DESELECT_DELAY_MS )
        self._collapse_timer.start( delay )

    def _apply_collapse( self ):
        item = self._collapse_to
        self._collapse_to = None
        if item is None:
            return
        try:
            item.text( 1 )
        except RuntimeError:
            return
        if self._collapse_deselect:
            self._just_deselected = item
            self.clearSelection()
            return
        self.blockSignals( True )
        self.clearSelection()
        self.blockSignals( False )
        item.setSelected( True )

    def mouseDoubleClickEvent( self, event ):
        self._collapse_timer.stop()
        self._collapse_to = None
        deselected = self._just_deselected
        self._just_deselected = None
        if deselected is not None and self.itemAt( _event_pos( event ) ) is deselected:
            deselected.setSelected( True )
        item = self._lock_column_item( event )
        if item is not None:
            self._lock_down = True
            if not item.icon( 0 ).isNull():
                self._start_lock_drag( item )
            return
        super( _InfluenceTree, self ).mouseDoubleClickEvent( event )


class _InfluenceHeader( QtWidgets.QHeaderView ):

    lock_clicked = QtCore.Signal( int )
    name_clicked = QtCore.Signal( int, bool, bool )

    def __init__( self, parent=None ):
        super( _InfluenceHeader, self ).__init__( QtCore.Qt.Orientation.Horizontal, parent )
        self.locks = []
        self.names = []
        self.selected = set()
        self.cell_mode = False
        self.setSectionsClickable( False )
        self.setHighlightSections( False )
        self.setSectionResizeMode( QtWidgets.QHeaderView.ResizeMode.Fixed )
        self.setDefaultSectionSize( _WT_CELL_W )
        self.setMinimumSectionSize( 10 )
        self.setFixedHeight( _WT_HEAD_TEXT_H + _WT_LOCK_H )

    def fit_names( self, names ):
        if names is not None:
            self.names = list( names )
        metrics = self.fontMetrics()
        longest = max( [metrics.horizontalAdvance( _wt_header_text( n ) ) for n in self.names] or [0] )
        height = max( _WT_HEAD_TEXT_H, longest + 10 ) + _WT_LOCK_H
        if height != self.height():
            self.setFixedHeight( height )
            table = self.parentWidget()
            if isinstance( table, QtWidgets.QTableView ):
                table.updateGeometries()

    def _in_lock_area( self, pos ):
        return pos.y() >= self.height() - _WT_LOCK_H

    def mousePressEvent( self, event ):
        pos = _event_pos( event )
        index = self.logicalIndexAt( pos )
        if index >= 0:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if self._in_lock_area( pos ):
                    self.lock_clicked.emit( index )
                else:
                    mods = event.modifiers()
                    self.name_clicked.emit( index,
                                            bool( mods & QtCore.Qt.KeyboardModifier.ControlModifier ),
                                            bool( mods & QtCore.Qt.KeyboardModifier.ShiftModifier ) )
            return
        table = self.parentWidget()
        if event.button() == QtCore.Qt.MouseButton.LeftButton and isinstance( table, _WeightTable ):
            table.clear_all_selection()
            return
        super( _InfluenceHeader, self ).mousePressEvent( event )

    def mouseDoubleClickEvent( self, event ):
        pos = _event_pos( event )
        index = self.logicalIndexAt( pos )
        if index >= 0:
            if event.button() == QtCore.Qt.MouseButton.LeftButton and not self._in_lock_area( pos ):
                self.lock_clicked.emit( index )
            return
        super( _InfluenceHeader, self ).mouseDoubleClickEvent( event )

    def paintSection( self, painter, rect, index ):
        if not rect.isValid():
            return
        painter.save()
        selected = index in self.selected
        if index >= len( _wt_grid["infs"] ):
            bg_color, sel_color, lock_sel_text = _WT_INF_EXTRA_COLOR, _WT_INF_EXTRA_SEL_COLOR, _WT_INF_EXTRA_LOCK_SEL_TEXT_COLOR
        elif self.cell_mode:
            bg_color, sel_color, lock_sel_text = _WT_INF_CELL_COLOR, _WT_INF_CELL_SEL_COLOR, _WT_INF_CELL_LOCK_SEL_TEXT_COLOR
        else:
            bg_color, sel_color, lock_sel_text = _WT_INF_COLOR, _WT_INF_SEL_COLOR, _WT_INF_LOCK_SEL_TEXT_COLOR
        painter.fillRect( rect, _qcolor( sel_color if selected else bg_color ) )
        painter.setPen( QtGui.QColor( 43, 43, 43 ) )
        painter.drawLine( rect.topRight(), rect.bottomRight() )
        split_y = rect.bottom() - _WT_LOCK_H
        painter.drawLine( rect.left(), split_y, rect.right(), split_y )

        name = self.model().headerData( index, QtCore.Qt.Orientation.Horizontal,
                                        QtCore.Qt.ItemDataRole.DisplayRole ) or ""
        locked = index < len( self.locks ) and self.locks[index]
        if selected:
            painter.setPen( _qcolor( lock_sel_text ) if locked else QtGui.QColor( 20, 20, 20 ) )
        else:
            painter.setPen( _qcolor( _WT_INF_LOCK_TEXT_COLOR ) if locked else QtGui.QColor( 230, 230, 230 ) )
        text_h = rect.height() - _WT_LOCK_H
        painter.translate( rect.left(), rect.top() + text_h )
        painter.rotate( -90 )
        area = QtCore.QRect( 4, 0, text_h - 8, rect.width() )
        painter.drawText( area, int( QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter ),
                          _wt_header_text( name ) )
        painter.restore()

        if index < len( self.locks ):
            pix = _lock_pixmap( self.locks[index] )
            x = rect.left() + ( rect.width() - 16 ) // 2
            y = rect.bottom() - _WT_LOCK_H + ( _WT_LOCK_H - 16 ) // 2 + 1
            painter.drawPixmap( x, y, 16, 16, pix )


class _WeightDelegate( QtWidgets.QStyledItemDelegate ):

    def createEditor( self, parent, option, index ):
        editor = QtWidgets.QLineEdit( parent )
        validator = QtGui.QDoubleValidator( 0.0, 1.0, 3, editor )
        validator.setNotation( QtGui.QDoubleValidator.Notation.StandardNotation )
        validator.setLocale( QtCore.QLocale.c() )
        editor.setValidator( validator )
        editor.setFrame( False )
        editor.setAlignment( QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter )
        return editor

    def setEditorData( self, editor, index ):
        editor.setText( index.data() or "" )
        editor.selectAll()

    def setModelData( self, editor, model, index ):
        try:
            value = min( max( float( editor.text() ), 0.0 ), 1.0 )
        except ValueError:
            return
        model.setData( index, "%.3f" % value )


class _WeightTable( QtWidgets.QTableWidget ):

    def clear_all_selection( self ):
        self.clearSelection()
        _wt_clear_influence_selection()

    def mousePressEvent( self, event ):
        clear = ( event.button() == QtCore.Qt.MouseButton.LeftButton
                  and event.modifiers() == QtCore.Qt.KeyboardModifier.NoModifier
                  and not self.indexAt( _event_pos( event ) ).isValid() )
        super( _WeightTable, self ).mousePressEvent( event )
        if clear:
            self.clear_all_selection()

    def __init__( self, parent=None ):
        super( _WeightTable, self ).__init__( parent )
        self._clear_targets = [self.verticalHeader().viewport()]
        corner = self.findChild( QtWidgets.QAbstractButton )
        if corner is not None:
            self._clear_targets.append( corner )
        for w in self._clear_targets:
            w.installEventFilter( self )

    def eventFilter( self, obj, event ):
        if obj in self._clear_targets:
            etype = event.type()
            if etype == QtCore.QEvent.Type.MouseButtonPress:
                if event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self.clear_all_selection()
                return True
            if etype in ( QtCore.QEvent.Type.MouseButtonRelease, QtCore.QEvent.Type.MouseButtonDblClick,
                          QtCore.QEvent.Type.MouseMove ):
                return True
        return super( _WeightTable, self ).eventFilter( obj, event )

    def keyPressEvent( self, event ):
        text = event.text()
        index = self.currentIndex()
        if ( text and text in "0123456789." and index.isValid()
                and self.state() != QtWidgets.QAbstractItemView.State.EditingState
                and index.flags() & QtCore.Qt.ItemFlag.ItemIsEditable ):
            triggers = self.editTriggers()
            any_key = QtWidgets.QAbstractItemView.EditTrigger.AnyKeyPressed
            self.setEditTriggers( triggers | any_key )
            try:
                opened = self.edit( index, any_key, event )
            finally:
                self.setEditTriggers( triggers )
            if opened:
                return
        super( _WeightTable, self ).keyPressEvent( event )


def _dedup( seq ):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add( x )
            out.append( x )
    return out


def _ui():
    win = _win[0]
    if win is None or not isValid( win ):
        return None
    return win


def _skin_cluster_name():
    ui = _ui()
    return ui.sc_field.text() if ui else ""


def _related_skin_cluster( obj ):
    return mel.eval( 'findRelatedSkinCluster "%s"' % obj ) or ""


def _main_progress_bar():
    return mel.eval( "$_stTmp = $gMainProgressBar" )


def _active_set():
    active = ""
    if cmds.optionVar( exists="ST_ActiveSet" ):
        active = cmds.optionVar( q="ST_ActiveSet" ) or ""
    skin = _skin_cluster_name()
    if not active:
        return ""
    if cmds.objExists( active ) and cmds.nodeType( active ) == "objectSet":
        return active
    return "skinningToolsSet_" + skin + "_fullSet"


def _inf_items():
    ui = _ui()
    if not ui:
        return []
    tree = ui.tree
    return [tree.topLevelItem( i ) for i in range( tree.topLevelItemCount() )]


def _inf_selected():
    return [it.text( 1 ) for it in _inf_items() if it.isSelected()]


def _inf_all():
    return [it.text( 1 ) for it in _inf_items()]


def _refresh_lock_button( item ):
    name = item.text( 1 )
    if not cmds.objExists( name ) or not cmds.attributeQuery( "liw", node=name, exists=True ):
        item.setIcon( 0, QtGui.QIcon() )
        item.setForeground( 1, QtGui.QBrush() )
        item.setData( 1, QtCore.Qt.ItemDataRole.UserRole, False )
        return
    locked = cmds.getAttr( name + ".liw" )
    item.setData( 1, QtCore.Qt.ItemDataRole.UserRole, bool( locked ) )
    item.setIcon( 0, QtGui.QIcon( _lock_pixmap( locked ) ) )
    item.setToolTip( 0, _tr( "Lock / unlock the weights of {}." ).format( name ) )
    item.setForeground( 1, QtGui.QBrush( _qcolor( _LOCKED_INF_TEXT_COLOR ) ) if locked
                        else QtGui.QBrush() )


def _lock_button_pressed( influence ):
    lock = 0 if cmds.getAttr( influence + ".liw" ) else 1
    targets = [influence]
    selected = _inf_selected()
    if influence in selected:
        targets = selected
    for i in targets:
        cmds.setAttr( i + ".liw", lock )
    _sync_locks()


_lock_drag_changed = [False]


def _lock_button_dragged( source, target ):
    if not cmds.objExists( source + ".liw" ) or not cmds.objExists( target + ".liw" ):
        return
    lock = cmds.getAttr( source + ".liw" )
    if cmds.getAttr( target + ".liw" ) != lock:
        cmds.setAttr( target + ".liw", lock )
        _lock_drag_changed[0] = True
        for item in _inf_items():
            if item.text( 1 ) == target:
                _refresh_lock_button( item )
                break


def _lock_drag_finished():
    if _lock_drag_changed[0]:
        _lock_drag_changed[0] = False
        _sync_locks()


def _tree_item_double_clicked( item, column ):
    if item.icon( 0 ).isNull():
        return
    ui = _ui()
    name = item.text( 1 )
    before = ui.tree.press_selection if ui else []
    if name in before and len( before ) > 1:
        _select_list_items( before )
        paint_weights_function( "paint" )
    _lock_button_pressed( name )


def _is_set_for_new_selection( skin_cluster, set_name ):
    selection = cmds.ls( sl=True, o=True ) or []
    new_selection_int = 1
    if selection:
        selection_shape = cmds.listRelatives( selection[0], s=True, ni=True ) or []
        if not selection_shape:
            return 1
        if len( selection_shape ) > 1:
            cmds.warning( _tr( "Selected object has multiple shapes. This can produce undesirable results." ) )

        set_stripped = ( set_name or "" ).replace( "skinningToolsSet_", "", 1 )
        buf = set_stripped.split( "_" )
        if buf and buf[0] == skin_cluster:
            new_selection_int = 1
        else:
            new_selection_int = 0

        if not new_selection_int:
            cmds.optionVar( stringValue=["ST_ActiveSet",
                                         "skinningToolsSet_" + skin_cluster + "_fullSet"] )
    return new_selection_int


def _fill_influence_list( names, selected ):
    ui = _ui()
    if not ui:
        return
    tree = ui.tree
    same_names = [item.text( 1 ) for item in _inf_items()] == list( names )
    scroll = tree.verticalScrollBar().value()
    tree.blockSignals( True )
    tree.clear()
    for name in names:
        item = QtWidgets.QTreeWidgetItem( ["", name] )
        tree.addTopLevelItem( item )
        _refresh_lock_button( item )
        if name in selected:
            item.setSelected( True )
    tree.blockSignals( False )
    if same_names:
        tree.doItemsLayout()
        tree.verticalScrollBar().setValue( scroll )
    _wt_sync_header_selection()


def list_smooth_skin_influences( skin_cluster, set_name ):
    ui = _ui()
    if not skin_cluster or not ui:
        return
    if not cmds.objExists( skin_cluster ):
        cmds.error( _tr( "Skin cluster specified incorrectly. Try again." ) )
        return

    selected_item = _inf_selected()
    is_set_for_new = _is_set_for_new_selection( skin_cluster, set_name )

    full = "skinningToolsSet_" + skin_cluster + "_fullSet"
    if set_name == full or set_name == "" or not is_set_for_new:
        influences = cmds.skinCluster( skin_cluster, q=True, inf=True ) or []
    else:
        influences = cmds.sets( set_name, q=True ) or []
        all_sc_inf = cmds.skinCluster( skin_cluster, q=True, inf=True ) or []
        combined = _dedup( list( influences ) + list( all_sc_inf ) )
        if len( combined ) != len( all_sc_inf ):
            cmds.warning( _tr( 'Set does not belong to current skinCluster. '
                               'Try again or use "Complete Set".' ) )
            return

    influences = list( influences )

    order = ui.list_order()
    if order == "Alphabetical":
        influences = sorted( influences )
    elif order == "Reverse Alphabetical":
        influences = sorted( influences )[::-1]
    elif order == "Reverse Graph Order":
        influences = influences[::-1]
    elif order in ( "Hold", "Reverse Hold" ):
        held = [i for i in influences if cmds.getAttr( i + ".liw" )]
        non_held = [i for i in influences if not cmds.getAttr( i + ".liw" )]
        influences = non_held + held if order == "Hold" else held + non_held

    _fill_influence_list( influences, selected_item )

    _wt_apply_states()


def select_full_set():
    skin = _skin_cluster_name()
    cmds.optionVar( stringValue=["ST_ActiveSet", "skinningToolsSet_" + skin + "_fullSet"] )
    list_smooth_skin_influences( skin, _active_set() )


def toggle_hold_influence_weight( influences ):
    if not influences:
        return
    for influence in influences:
        cmds.setAttr( influence + ".liw", 0 if cmds.getAttr( influence + ".liw" ) else 1 )
    list_smooth_skin_influences( _skin_cluster_name(), _active_set() )


def hold_all_influences( hold_on_off ):
    all_influences = _inf_all()
    if not all_influences:
        return
    for i in all_influences:
        cmds.setAttr( i + ".liw", 1 if hold_on_off else 0 )
    list_smooth_skin_influences( _skin_cluster_name(), _active_set() )


def _sync_locks():
    for item in _inf_items():
        _refresh_lock_button( item )
    _wt_apply_states()


def _to_vertices( components ):
    verts = cmds.polyListComponentConversion( components, fv=True, fe=True, ff=True, tv=True ) or []
    return cmds.ls( verts, fl=True ) or []


def set_weights( value ):
    if _wt_set_selected_cells( value ):
        return

    selected_components = cmds.ls( sl=True ) or []
    if not selected_components:
        print( _tr( "Select some points and try again." ) + "\n" )
        return
    if any( re.search( r"\.(e|f)\[", c ) for c in selected_components ):
        selected_components = _to_vertices( selected_components )
        selected_components_flat = selected_components
    else:
        selected_components_flat = cmds.ls( sl=True, fl=True ) or []
    selected_object = cmds.ls( sl=True, o=True ) or []
    if selected_object and selected_components[0] == selected_object[0]:
        print( _tr( "Select some points and try again." ) + "\n" )
        return

    influences = _inf_selected()
    if not influences:
        print( _tr( "Select one or more influences from the UI list and try again." ) + "\n" )
        return

    skin_cluster = _related_skin_cluster( selected_object[0] )
    if not skin_cluster:
        print( _tr( "Select one or more influences from the UI list and try again." ) + "\n" )
        return
    if skin_cluster != _skin_cluster_name():
        cmds.error( _tr( "Selected object is not loaded into UI. Try again." ) + "\n" )
        return

    for i in influences:
        if cmds.getAttr( i + ".lockInfluenceWeights" ):
            print( _tr( 'Influence {} is locked. Toggle "Hold" off and try again.' ).format( i ) + "\n" )
            return
        cmds.skinPercent( skin_cluster, selected_components, relative=True, tv=[i, value] )
        for s in selected_components_flat:
            cur = cmds.skinPercent( skin_cluster, s, t=i, q=True )
            if cur > 1.0:
                cmds.skinPercent( skin_cluster, s, tv=[i, 1.0] )
            elif cur < 0.0:
                cmds.skinPercent( skin_cluster, s, tv=[i, 0.0] )

    weight_table_refresh_values()


_weight_clip = []
_cell_clip = []


def _ordered_points():
    points = []
    seen = set()
    for c in cmds.ls( os=True, fl=True ) or []:
        if re.search( r"\.(e|f)\[", c ):
            verts = _to_vertices( [c] )
        elif re.search( r"\.(vtx|cv|pt)\[", c ):
            verts = [c]
        else:
            continue
        for v in verts:
            if v not in seen:
                seen.add( v )
                points.append( v )
    return points


def _point_skin( point, cache ):
    obj = point.split( ".", 1 )[0]
    if obj not in cache:
        skin_cluster = _related_skin_cluster( obj )
        infs = ( cmds.skinCluster( skin_cluster, q=True, inf=True ) or [] ) if skin_cluster else []
        cache[obj] = ( skin_cluster, infs )
    return cache[obj]


def _point_values( skin_cluster, point ):
    values = cmds.skinPercent( skin_cluster, point, q=True, value=True )
    return list( values ) if isinstance( values, (list, tuple) ) else [values]


def _paste_label( cell_mode=False ):
    clip = _cell_clip if cell_mode else _weight_clip
    return _tr( "Paste" ) + ( " (%d)" % len( clip ) if clip else "" )


def copy_weights():
    if _wt_cell_mode():
        _copy_cells()
    else:
        _copy_points()


def paste_weights():
    if _wt_cell_mode():
        _paste_cells()
    else:
        _paste_points()


def _copy_cells():
    cells = _wt_ordered_cells()
    skin_cluster = _wt_grid["skin"]
    _cell_clip[:] = [cmds.skinPercent( skin_cluster, vert, t=inf, q=True ) for vert, inf in cells]
    _wt_update_status()
    print( _tr( "Copied {} cell values." ).format( len( _cell_clip ) ) + "\n" )


def _paste_cells():
    if not _cell_clip:
        cmds.warning( _tr( "Copy the cell values first." ) )
        return
    cells = _wt_ordered_cells()
    if len( _cell_clip ) == 1:
        pairs = [(c, _cell_clip[0]) for c in cells]
    else:
        pairs = list( zip( cells, _cell_clip ) )
        if len( cells ) != len( _cell_clip ):
            cmds.warning( _tr( "Copied {} cells but {} are selected. Pasted to the first {}." ).format(
                len( _cell_clip ), len( cells ), len( pairs ) ) )
    unlocked = _wt_apply_edits( [c for c, _ in pairs], 1, 0.0, values=dict( pairs ), unlock=True )
    if unlocked:
        print( _tr( "Unlocked influences: {}" ).format( ", ".join( unlocked ) ) + "\n" )
    print( _tr( "Pasted the values to {} cells." ).format( len( pairs ) ) + "\n" )
    weight_table_refresh_values()


def _copy_points():
    points = _ordered_points()
    if not points:
        cmds.warning( _tr( "Select vertices one by one in order and try again." ) )
        return
    cache = {}
    clip = []
    for point in points:
        skin_cluster, infs = _point_skin( point, cache )
        if not skin_cluster:
            cmds.warning( _tr( "{} has no skinCluster." ).format( point.split( ".", 1 )[0] ) )
            return
        values = _point_values( skin_cluster, point )
        clip.append( {i: v for i, v in zip( infs, values ) if v > 0.0} )
    _weight_clip[:] = clip
    _wt_update_status()
    print( _tr( "Copied the weights of {} vertices." ).format( len( clip ) ) + "\n" )


def _paste_points():
    if not _weight_clip:
        cmds.warning( _tr( "Copy the weights first." ) )
        return
    points = _ordered_points()
    if not points:
        cmds.warning( _tr( "Select vertices one by one in order and try again." ) )
        return
    if len( _weight_clip ) == 1:
        pairs = [(p, _weight_clip[0]) for p in points]
    else:
        pairs = list( zip( points, _weight_clip ) )
        if len( points ) != len( _weight_clip ):
            cmds.warning( _tr( "Copied {} vertices but {} are selected. Pasted to the first {}." ).format(
                len( _weight_clip ), len( points ), len( pairs ) ) )

    cache = {}
    writes = {}
    unlock = []
    for point, weights in pairs:
        skin_cluster, infs = _point_skin( point, cache )
        if not skin_cluster:
            cmds.warning( _tr( "{} has no skinCluster." ).format( point.split( ".", 1 )[0] ) )
            return
        missing = [i for i in weights if i not in infs]
        if missing:
            cmds.warning( _tr( "{} does not have these influences: {}" ).format( skin_cluster, ", ".join( missing ) ) )
            return
        old = _point_values( skin_cluster, point )
        changed = [(inf, weights.get( inf, 0.0 )) for inf, value in zip( infs, old )
                   if abs( weights.get( inf, 0.0 ) - value ) > 1e-9]
        if not changed:
            continue
        writes.setdefault( skin_cluster, [] ).append( (point, changed) )
        for inf, _ in changed:
            if inf not in unlock and cmds.objExists( inf + ".liw" ) and cmds.getAttr( inf + ".liw" ):
                unlock.append( inf )

    if writes:
        cmds.undoInfo( openChunk=True )
        try:
            for inf in unlock:
                cmds.setAttr( inf + ".liw", 0 )
            for skin_cluster, items in writes.items():
                normalize = cmds.getAttr( skin_cluster + ".normalizeWeights" )
                cmds.setAttr( skin_cluster + ".normalizeWeights", 0 )
                try:
                    for point, changed in items:
                        cmds.skinPercent( skin_cluster, point, transformValue=changed, normalize=False )
                finally:
                    cmds.setAttr( skin_cluster + ".normalizeWeights", normalize )
        finally:
            cmds.undoInfo( closeChunk=True )
    if unlock:
        print( _tr( "Unlocked influences: {}" ).format( ", ".join( unlock ) ) + "\n" )
    print( _tr( "Pasted the weights to {} vertices." ).format( len( pairs ) ) + "\n" )
    weight_table_refresh_values()


def _wt_short_name( node ):
    return node.split( "|" )[-1].split( ":" )[-1]


def _wt_header_text( name ):
    return name[:_WT_NAME_MAX_CHARS]


def _wt_row_label( component ):
    return component.split( "[", 1 )[1].rstrip( "]" ).replace( "][", "," )


def _wt_selected_components():
    owner, names = _wt_selected_points()
    if not names and not any( "." in item for item in cmds.ls( sl=True ) or [] ):
        owner, names = _wt_object_points()
    return owner, names


def _wt_object_points():
    for obj in cmds.ls( sl=True, o=True ) or []:
        skin_cluster = _related_skin_cluster( obj )
        if not skin_cluster:
            continue
        shapes = cmds.listRelatives( obj, s=True, ni=True, f=True ) or [obj]
        if cmds.nodeType( shapes[0] ) == "mesh":
            count = cmds.polyEvaluate( shapes[0], v=True )
            names = ["%s.vtx[%d]" % (obj, n) for n in range( min( count, _WT_MAX_ROWS ) )]
        else:
            sets = cmds.listConnections( skin_cluster, type="objectSet" ) or []
            members = ( cmds.sets( sets[0], q=True ) or [] ) if sets else []
            points = ( cmds.filterExpand( members, sm=(28, 31, 46) ) or [] ) if members else []
            count = len( points )
            names = points[:_WT_MAX_ROWS]
        if count > _WT_MAX_ROWS:
            print( _tr( "Weight table: showing the first {} of {} points." ).format( _WT_MAX_ROWS, count ) + "\n" )
        return obj, names
    return "", []


def _wt_selected_points():
    owner = ""
    names = []
    conv_verts = set()
    for item in cmds.ls( os=True ) or []:
        if "." not in item:
            continue
        obj, comp = item.split( ".", 1 )
        if owner and obj != owner:
            continue
        room = max( _WT_MAX_ROWS - len( names ), 0 )
        m = _VTX_RANGE.match( comp )
        if m:
            first = int( m.group( 1 ) )
            last = int( m.group( 2 ) ) if m.group( 2 ) else first
            for n in range( first, min( last + 1, first + room ) ):
                names.append( "%s.vtx[%d]" % (obj, n) )
        elif comp.startswith( ("cv[", "pt[") ):
            flat = cmds.ls( item, fl=True ) or []
            names.extend( flat[:room] )
        elif comp.startswith( ("e[", "f[") ):
            verts = cmds.ls( cmds.polyListComponentConversion( item, fe=True, ff=True, tv=True ) or [],
                             fl=True ) or []
            verts = [v for v in verts if v not in conv_verts][:room]
            conv_verts.update( verts )
            names.extend( verts )
        else:
            continue
        owner = obj
    if len( names ) >= _WT_MAX_ROWS:
        print( _tr( "Weight table: showing the first {} selected points." ).format( _WT_MAX_ROWS ) + "\n" )
    return owner, names


def _wt_read_mesh( skin_cluster, verts, all_infs ):
    obj = verts[0].split( ".", 1 )[0]
    indices = []
    for v in verts:
        m = _VTX_RANGE.match( v.split( ".", 1 )[-1] )
        if not v.startswith( obj + "." ) or not m or m.group( 2 ):
            return None
        indices.append( int( m.group( 1 ) ) )
    shapes = cmds.listRelatives( obj, s=True, ni=True, f=True ) or [obj]
    try:
        sel = om2.MSelectionList()
        sel.add( skin_cluster )
        sel.add( shapes[0] )
        fn = oma2.MFnSkinCluster( sel.getDependNode( 0 ) )
        comp_fn = om2.MFnSingleIndexedComponent()
        comp = comp_fn.create( om2.MFn.kMeshVertComponent )
        order = sorted( set( indices ) )
        comp_fn.addElements( order )
        values, count = fn.getWeights( sel.getDagPath( 1 ), comp )
    except RuntimeError:
        return None
    if count != len( all_infs ) or len( values ) != count * len( order ):
        return None
    by_index = {}
    for k, index in enumerate( order ):
        by_index[index] = dict( zip( all_infs, values[k * count:(k + 1) * count] ) )
    return {v: by_index[i] for v, i in zip( verts, indices )}


def _wt_read( skin_cluster, verts ):
    all_infs = cmds.skinCluster( skin_cluster, q=True, inf=True ) or []
    weights = _wt_read_mesh( skin_cluster, verts, all_infs ) if verts else {}
    if weights is None:
        weights = {}
        for v in verts:
            w = cmds.skinPercent( skin_cluster, v, q=True, value=True )
            if not isinstance( w, (list, tuple) ):
                w = [w]
            weights[v] = dict( zip( all_infs, w ) )
    infs = [i for i in all_infs if any( weights[v].get( i, 0.0 ) > _WT_EPS for v in verts )]
    return infs, weights


def _wt_lock_states():
    return {i: bool( cmds.getAttr( i + ".liw" ) ) if cmds.objExists( i + ".liw" ) else False
            for i in _wt_columns()}


def _wt_columns():
    return _wt_grid["infs"] + _wt_grid["extra"]


def _wt_extra_infs( skin_cluster, infs ):
    if not skin_cluster or skin_cluster != _skin_cluster_name():
        return []
    shown = {_wt_list_name( i ) for i in infs}
    selected = set( _inf_selected() )
    return [n for n in _inf_all() if n in selected and n not in shown]


def _wt_index_cells( indexes ):
    verts = _wt_grid["verts"]
    infs = _wt_grid["infs"]
    return [(verts[r], infs[c]) for r, c in sorted( ( i.row(), i.column() ) for i in indexes )
            if r < len( verts ) and c < len( infs )]


def _wt_selected_cells():
    ui = _ui()
    if not ui:
        return []
    return _wt_index_cells( ui.table.selectionModel().selectedIndexes() )


def _wt_cell_mode():
    ui = _ui()
    return bool( ui ) and ui.table.selectionModel().hasSelection()


_wt_cell_order = []


def _wt_track_cell_order( selected, deselected ):
    ui = _ui()
    if not ui or ui.updating:
        return
    gone = set( _wt_index_cells( deselected.indexes() ) )
    _wt_cell_order[:] = [c for c in _wt_cell_order if c not in gone]
    for cell in _wt_index_cells( selected.indexes() ):
        if cell not in _wt_cell_order:
            _wt_cell_order.append( cell )


def _wt_ordered_cells():
    cells = _wt_selected_cells()
    current = set( cells )
    ordered = [c for c in _wt_cell_order if c in current]
    done = set( ordered )
    return ordered + [c for c in cells if c not in done]


def _wt_selection_snapshot():
    ui = _ui()
    model = ui.table.selectionModel()
    root = QtCore.QModelIndex()
    verts = [v for r, v in enumerate( _wt_grid["verts"] ) if model.isRowSelected( r, root )]
    infs = [i for c, i in enumerate( _wt_grid["infs"] ) if model.isColumnSelected( c, root )]
    return set( _wt_selected_cells() ), set( verts ), set( infs )


def _wt_restore_selection( snapshot ):
    ui = _ui()
    cells, sel_verts, sel_infs = snapshot
    table = ui.table
    model = table.selectionModel()
    flag = QtCore.QItemSelectionModel.SelectionFlag.Select
    for r, v in enumerate( _wt_grid["verts"] ):
        for c, i in enumerate( _wt_grid["infs"] ):
            if (v, i) in cells or v in sel_verts or i in sel_infs:
                model.select( table.model().index( r, c ), flag )


def _wt_apply_states():
    ui = _ui()
    if not ui:
        return
    table = ui.table
    locks = _wt_lock_states()
    editable = ( QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
                 | QtCore.Qt.ItemFlag.ItemIsEditable )
    read_only = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled
    lock_brush = QtGui.QBrush( _qcolor( _WT_CELL_LOCK_COLOR ) )
    lock_text_brush = QtGui.QBrush( _qcolor( _WT_CELL_LOCK_TEXT_COLOR ) )
    ui.updating = True
    try:
        for c, inf in enumerate( _wt_grid["infs"] ):
            locked = locks[inf]
            for r in range( len( _wt_grid["verts"] ) ):
                item = table.item( r, c )
                if item is None:
                    continue
                item.setFlags( read_only if locked else editable )
                item.setBackground( lock_brush if locked else QtGui.QBrush() )
                item.setForeground( lock_text_brush if locked else QtGui.QBrush() )
    finally:
        ui.updating = False
    ui.inf_header.locks = [locks[i] for i in _wt_columns()]
    ui.inf_header.viewport().update()
    _wt_sync_header_selection()


def weight_table_refresh( *_ ):
    ui = _ui()
    if not ui:
        return
    table = ui.table
    snapshot = _wt_selection_snapshot()
    ui.updating = True
    try:
        table.clearSelection()
        table.setRowCount( 0 )
        table.setColumnCount( 0 )
        _wt_grid.update( skin="", verts=[], infs=[], extra=[] )
        table.horizontalHeader().setVisible( False )
        table.verticalHeader().setVisible( False )

        owner, verts = _wt_selected_components()
        skin_cluster = _related_skin_cluster( owner ) if owner else ""
        if not skin_cluster or not verts:
            return
        try:
            infs, weights = _wt_read( skin_cluster, verts )
        except RuntimeError:
            return

        extra = _wt_extra_infs( skin_cluster, infs )
        columns = infs + extra
        table.setColumnCount( len( columns ) )
        table.setRowCount( len( verts ) )
        for c, inf in enumerate( columns ):
            head = QtWidgets.QTableWidgetItem( _wt_short_name( inf ) )
            table.setHorizontalHeaderItem( c, head )
        ui.inf_header.fit_names( [_wt_short_name( inf ) for inf in columns] )
        align = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        for r, v in enumerate( verts ):
            head = QtWidgets.QTableWidgetItem( _wt_row_label( v ) )
            head.setTextAlignment( align )
            table.setVerticalHeaderItem( r, head )
            for c, inf in enumerate( infs ):
                item = QtWidgets.QTableWidgetItem( "%.3f" % weights[v].get( inf, 0.0 ) )
                item.setTextAlignment( align )
                table.setItem( r, c, item )
            for c in range( len( infs ), len( columns ) ):
                item = QtWidgets.QTableWidgetItem( "" )
                item.setFlags( QtCore.Qt.ItemFlag.NoItemFlags )
                table.setItem( r, c, item )
        _wt_grid.update( skin=skin_cluster, verts=list( verts ), infs=list( infs ), extra=extra )
        _wt_restore_selection( snapshot )
        table.horizontalHeader().setVisible( True )
        table.verticalHeader().setVisible( True )
    finally:
        ui.updating = False
        _wt_apply_states()
        _wt_update_status()


def _wt_update_status( *_ ):
    ui = _ui()
    if not ui:
        return
    cell_mode = _wt_cell_mode()
    if getattr( ui, "paste_btn", None ):
        ui.paste_btn.setText( _paste_label( cell_mode ) )
    header = getattr( ui, "inf_header", None )
    if header and header.cell_mode != cell_mode:
        header.cell_mode = cell_mode
        header.viewport().update()
    if cell_mode:
        text, color = "Status: Cell mode", _WT_STATUS_CELL_COLOR
    elif any( re.search( r"\.(vtx|cv|pt|e|f)\[", c ) for c in cmds.ls( sl=True ) or [] ):
        text, color = "Status: Vertex mode", _WT_STATUS_VTX_COLOR
    else:
        text, color = "Status: ", _WT_STATUS_COLOR
    ui.status_label.setText( _tr( text ) )
    ui.status_label.setStyleSheet( "QLabel { color: %s; padding-left: 4px; }" % _rgb( color ) )


def weight_table_refresh_values( *_ ):
    ui = _ui()
    if not ui:
        return
    skin_cluster = _wt_grid["skin"]
    verts = _wt_grid["verts"]
    if not verts or not cmds.objExists( skin_cluster ):
        QtCore.QTimer.singleShot( 0, weight_table_refresh )
        return
    try:
        infs, weights = _wt_read( skin_cluster, verts )
    except RuntimeError:
        QtCore.QTimer.singleShot( 0, weight_table_refresh )
        return
    if set( infs ) - set( _wt_grid["infs"] ):
        QtCore.QTimer.singleShot( 0, weight_table_refresh )
        return
    ui.updating = True
    try:
        for r, v in enumerate( verts ):
            for c, inf in enumerate( _wt_grid["infs"] ):
                item = ui.table.item( r, c )
                if item is not None:
                    item.setText( "%.3f" % weights[v].get( inf, 0.0 ) )
    finally:
        ui.updating = False
    _sync_locks()


def _wt_lock_pressed( column ):
    infs = _wt_columns()
    if column >= len( infs ) or not cmds.objExists( infs[column] + ".liw" ):
        return
    inf = infs[column]
    cmds.setAttr( inf + ".liw", 0 if cmds.getAttr( inf + ".liw" ) else 1 )
    _sync_locks()


def _wt_list_name( inf ):
    names = _inf_all()
    if inf in names:
        return inf
    short = inf.split( "|" )[-1]
    matches = [n for n in names if n.split( "|" )[-1] == short]
    return matches[0] if matches else ""


def _wt_sync_header_selection():
    ui = _ui()
    if not ui or not getattr( ui, "inf_header", None ):
        return
    selected = set( _inf_selected() )
    ui.inf_header.selected = {c for c, inf in enumerate( _wt_columns() )
                              if _wt_list_name( inf ) in selected}
    ui.inf_header.viewport().update()
    if _wt_grid["verts"] and _wt_extra_infs( _wt_grid["skin"], _wt_grid["infs"] ) != _wt_grid["extra"]:
        QtCore.QTimer.singleShot( 0, weight_table_refresh )


def _wt_clear_influence_selection():
    ui = _ui()
    if not ui or not ui.tree.selectedItems():
        return
    ui.tree.clearSelection()


def _wt_header_clicked( column, ctrl, shift ):
    infs = _wt_columns()
    if column >= len( infs ):
        return
    ui = _ui()
    if ui:
        ui.table.clearSelection()
    name = _wt_list_name( infs[column] )
    if not name:
        return
    current = _inf_selected()
    anchor = _wt_anchor[0]
    if shift and anchor is not None and anchor < len( infs ):
        lo, hi = sorted( ( anchor, column ) )
        names = [n for n in ( _wt_list_name( i ) for i in infs[lo:hi + 1] ) if n]
        if ctrl:
            names = current + [n for n in names if n not in current]
    elif ctrl:
        names = [n for n in current if n != name] if name in current else current + [name]
        _wt_anchor[0] = column
    else:
        names = [name]
        _wt_anchor[0] = column
    _select_list_items( names )
    paint_weights_function( "paint" )


def _wt_apply_edits( cells, set_mode, value, values=None, unlock=False ):
    skin_cluster = _wt_grid["skin"]
    all_infs = cmds.skinCluster( skin_cluster, q=True, inf=True ) or []
    held = [cmds.getAttr( n + ".liw" ) for n in all_infs]
    normalize = cmds.getAttr( skin_cluster + ".normalizeWeights" )
    unlocked = []
    if unlock:
        for _, inf in cells:
            k = all_infs.index( inf )
            if held[k]:
                held[k] = False
                unlocked.append( inf )

    by_vert = {}
    for vert, inf in cells:
        by_vert.setdefault( vert, [] ).append( all_infs.index( inf ) )

    writes = []
    for vert, targets in by_vert.items():
        old = cmds.skinPercent( skin_cluster, vert, q=True, value=True )
        if not isinstance( old, (list, tuple) ):
            old = [old]
        new = list( old )
        edited = []
        for k in targets:
            if held[k]:
                print( _tr( 'Influence {} is locked. Toggle "Hold" off and try again.' ).format( all_infs[k] )
                       + "\n" )
                continue
            v = values[(vert, all_infs[k])] if values is not None else value
            new[k] = min( max( v if set_mode == 1 else old[k] + v, 0.0 ), 1.0 )
            edited.append( k )
        if not edited:
            continue

        changed = [(all_infs[k], new[k]) for k in edited if abs( new[k] - old[k] ) > 1e-9]
        if changed:
            writes.append( (vert, changed) )

    if not writes:
        return []
    cmds.undoInfo( openChunk=True )
    try:
        for inf in unlocked:
            cmds.setAttr( inf + ".liw", 0 )
        for vert, changed in writes:
            cmds.skinPercent( skin_cluster, vert, transformValue=changed, normalize=bool( normalize ) )
    finally:
        cmds.undoInfo( closeChunk=True )
    return unlocked


def _wt_item_changed( item ):
    ui = _ui()
    if not ui or ui.updating:
        return
    r, c = item.row(), item.column()
    if r >= len( _wt_grid["verts"] ) or c >= len( _wt_grid["infs"] ):
        return
    try:
        value = float( item.text() )
    except ValueError:
        weight_table_refresh_values()
        return
    cell = (_wt_grid["verts"][r], _wt_grid["infs"][c])
    cells = _wt_selected_cells()
    if cell in cells:
        locks = _wt_lock_states()
        cells = [x for x in cells if not locks[x[1]]]
    else:
        cells = [cell]
    _wt_apply_edits( cells, 1, value )
    weight_table_refresh_values()


def _wt_set_selected_cells( value ):
    cells = _wt_selected_cells()
    if not cells:
        return False
    locks = _wt_lock_states()
    editable = [c for c in cells if not locks[c[1]]]
    if editable:
        _wt_apply_edits( editable, 2, value )
        weight_table_refresh_values()
    else:
        print( _tr( "The selected cells are locked. Unlock the influences and try again." ) + "\n" )
    return True


def select_influences( influence_list ):
    if not influence_list:
        cmds.error( _tr( "No influences selected." ) )
        return
    cmds.select( influence_list, r=True )


def add_influences():
    sel = cmds.ls( sl=True, o=True, type="transform" ) or []
    if not sel:
        return
    skin_cluster = _skin_cluster_name()
    all_influences = cmds.skinCluster( skin_cluster, q=True, inf=True ) or []
    for s in sel:
        if all_influences.count( s ):
            cmds.warning( _tr( "{} is already part of {}. Ignoring." ).format( s, skin_cluster ) )
            continue
        cmds.skinCluster( skin_cluster, e=True, dr=4, lw=True, wt=0, ai=s )
    list_smooth_skin_influences( skin_cluster, _active_set() )


def remove_influence():
    skin_cluster = _skin_cluster_name()
    sel = _inf_selected()
    if not cmds.objExists( skin_cluster ) or not sel:
        return

    if len( sel ) > 1:
        message = _tr( "Remove influences from {}?" ).format( skin_cluster )
    else:
        message = _tr( "Remove influence {} from {}?" ).format( sel[0], skin_cluster )
    yes, no = _tr( "Yes" ), _tr( "No" )
    confirm = cmds.confirmDialog(
        title=_tr( "Remove Influence" ), message=message,
        button=[yes, no], defaultButton=yes, cancelButton=no, dismissString=no)
    if confirm != yes:
        return

    for s in sel:
        cmds.skinCluster( skin_cluster, e=True, ri=s )

    list_smooth_skin_influences( skin_cluster, _active_set() )
    weight_table_refresh()


def remove_unused_influences():
    try:
        mel.eval( "removeUnusedInfluences" )
    finally:
        skin_cluster = _skin_cluster_name()
        if cmds.objExists( skin_cluster ):
            list_smooth_skin_influences( skin_cluster, _active_set() )
        weight_table_refresh()


def select_affected_points( skin_cluster ):
    if not cmds.objExists( skin_cluster ):
        cmds.warning( _tr( "Given skinCluster node is incorrect. Try again." ) )
        return

    influences = _inf_selected()
    if not influences:
        return

    skin_cluster_set = cmds.listConnections( skin_cluster, type="objectSet" ) or []
    components = cmds.sets( skin_cluster_set[0], q=True ) or []
    components = cmds.filterExpand( components, sm=(36, 28, 31, 46) ) or []

    progress = _main_progress_bar()
    cmds.progressBar( progress, edit=True, beginProgress=True, isInterruptable=True,
                      status=_tr( "Finding skinCluster points..." ),
                      maxValue=max( len( components ) * len( influences ), 1 ) )

    affected_points = []
    for i in influences:
        for c in components:
            inf_value = cmds.skinPercent( skin_cluster, c, t=i, q=True, v=True )
            if inf_value > 0.0:
                affected_points.append( c )
            if cmds.progressBar( progress, q=True, isCancelled=True ):
                break
            cmds.progressBar( progress, edit=True, step=1 )

    cmds.progressBar( progress, edit=True, endProgress=True )
    if affected_points:
        cmds.select( affected_points, r=True )


def _select_list_items( names ):
    ui = _ui()
    if not ui:
        return
    ui.tree.blockSignals( True )
    ui.tree.clearSelection()
    first = None
    for item in _inf_items():
        if item.text( 1 ) in names:
            item.setSelected( True )
            first = first or item
    ui.tree.blockSignals( False )
    ui.tree.viewport().update()
    if first is not None:
        ui.tree.scrollToItem( first )
    _wt_sync_header_selection()


def reveal_selected( influences, skin_cluster ):
    if not influences:
        cmds.warning( _tr( "No influences selected. Try again." ) )
        return
    all_influences = cmds.skinCluster( skin_cluster, q=True, inf=True ) or []
    bad_influences = []
    for selected in influences:
        if selected not in all_influences:
            cmds.warning( _tr( "{} is not an influence of {}." ).format( selected, skin_cluster ) )
            bad_influences.append( selected )
    if len( bad_influences ) == len( influences ):
        return
    _select_list_items( influences )


def update_popup( menu ):
    def add( label, func, enabled=True ):
        action = menu.addAction( _tr( label ) )
        action.setEnabled( enabled )
        action.triggered.connect( lambda *_: func() )

    add( "Hold/Unhold", lambda: toggle_hold_influence_weight( _inf_selected() ) )
    add( "Hold All", lambda: hold_all_influences( 1 ) )
    add( "Unhold All", lambda: hold_all_influences( 0 ) )
    menu.addSeparator()
    selected_item = _inf_selected()
    add( "Select Influences" if len( selected_item ) > 1 else "Select Influence",
         lambda: select_influences( _inf_selected() ), bool( selected_item ) )
    add( "Select affected points", lambda: select_affected_points( _skin_cluster_name() ) )
    menu.addSeparator()
    add( "Reveal selected influence",
         lambda: reveal_selected( cmds.ls( sl=True, o=True, type="transform" ) or [],
                                  _skin_cluster_name() ) )


def load_selection():
    ui = _ui()
    selection = cmds.ls( sl=True, o=True ) or []
    if not selection or not ui:
        return
    skin_cluster = _related_skin_cluster( selection[0] )
    if not skin_cluster:
        return
    ui.sc_field.setText( skin_cluster )
    list_smooth_skin_influences( skin_cluster, _active_set() )


def script_job_load():
    ui = _ui()
    if ui and ui.auto_load_action.isChecked():
        load_selection()


def _on_selection_changed( *_ ):
    if not _ui():
        return
    script_job_load()
    weight_table_refresh()


def paint_weights_function( function ):
    ui = _ui()
    ctx = cmds.currentCtx()
    if not ui or ctx != "artAttrSkinContext":
        if ui and function == "flood":
            cmds.warning( _tr( "Not in paint mode. Press Start Paint Mode before Flood." ) )
        return

    if function == "paint":
        cmds.artAttrCtx( ctx, e=True, opacity=ui.opac.value() )
        cmds.artAttrCtx( ctx, e=True, value=ui.val.value() )
        sel_joint = _inf_selected()
        if sel_joint:
            mel.eval( 'setSmoothSkinInfluence "%s"' % sel_joint[0] )
        operation = ui.current_operation()
        if operation:
            cmds.artAttrCtx( "artAttrSkinContext", e=True, sao=dict( _OPERATIONS )[operation] )

    elif function in ( "gaussian", "poly", "solid" ):
        cmds.artAttrCtx( "artAttrSkinContext", e=True, stP=function )

    elif function in ( "replace", "add", "smooth", "scale" ):
        name = function.capitalize()
        cmds.artAttrCtx( cmds.currentCtx(), e=True, sao=dict( _OPERATIONS )[name] )
        cmds.optionVar( sv=["ST_PaintMode", name] )

    elif function == "flood":
        if not _inf_selected():
            cmds.warning( _tr( "Select an influence." ) )
            return
        cmds.artAttrCtx( cmds.currentCtx(), e=True, clear=True )
        weight_table_refresh_values()

    elif function == "OpacityChange":
        v = ui.opac.value()
        cmds.artAttrCtx( cmds.currentCtx(), e=True, opacity=v )
        cmds.optionVar( fv=["ST_PSW_Opacity", v] )
    elif function == "ValueChange":
        v = ui.val.value()
        cmds.artAttrCtx( cmds.currentCtx(), e=True, value=v )
        cmds.optionVar( fv=["ST_PSW_Value", v] )


def set_val( mode, val ):
    ui = _ui()
    if not ui:
        return
    geometry = cmds.ls( sl=True ) or []
    cmds.select( cl=True )
    if mode == "add":
        ui.set_operation( "Add" )
    elif mode == "scl":
        ui.set_operation( "Scale" )
    ui.val.setValue( val )
    if geometry:
        cmds.select( geometry[0], r=True )
    paint_weights_function( "paint" )


def color_or_mono():
    _cm_tgl[0] = 1 - cmds.artAttrCtx( "artAttrSkinContext", q=True, useColorRamp=True )
    cmds.artAttrCtx( "artAttrSkinContext", e=True, useColorRamp=_cm_tgl[0] )


def _active_paint_influence( skin_cluster ):
    try:
        influence = cmds.artAttrSkinPaintCtx( "artAttrSkinContext", q=True, influence=True ) or ""
    except RuntimeError:
        influence = ""
    if influence and cmds.objExists( influence ):
        return influence
    if cmds.objExists( skin_cluster + ".ptt" ):
        sources = cmds.listConnections( skin_cluster + ".ptt", s=True, d=False ) or []
        sources = [s for s in sources if s != skin_cluster]
        if sources:
            return sources[0]
    return ""


def _select_active_paint_influence( skin_cluster ):
    influence = _active_paint_influence( skin_cluster )
    if not influence:
        return
    names = _inf_all()
    if influence not in names:
        short = influence.split( "|" )[-1]
        matches = [n for n in names if n.split( "|" )[-1] == short]
        if not matches:
            return
        influence = matches[0]
    _select_list_items( [influence] )


def enter_paint_mode():
    skin_cluster = _skin_cluster_name()
    if not cmds.objExists( skin_cluster ):
        return
    geometry = cmds.skinCluster( skin_cluster, q=True, g=True ) or []
    mel.eval( "changeSelectMode -object" )
    if geometry and cmds.objExists( geometry[0] ):
        cmds.select( geometry[0], r=True )
    panel = cmds.getPanel( wf=True )
    if panel and cmds.getPanel( to=panel ) == "modelPanel":
        cmds.modelEditor( panel, e=True, displayAppearance="smoothShaded", activeOnly=False )
    mel.eval( "ArtPaintSkinWeightsTool" )
    if not _inf_selected():
        _select_active_paint_influence( skin_cluster )
    paint_weights_function( "paint" )


def _manual_path( file_name ):
    source = _manual_path.__code__.co_filename
    return os.path.join( os.path.dirname( os.path.abspath( source ) ), file_name )


def _manual_web_view( parent ):
    try:
        try:
            from PySide6 import QtWebEngineCore, QtWebEngineWidgets
            page_class = QtWebEngineCore.QWebEnginePage
        except ImportError:
            from PySide2 import QtWebEngineWidgets
            page_class = QtWebEngineWidgets.QWebEnginePage
    except Exception:
        return None

    class _ManualPage( page_class ):
        def acceptNavigationRequest( self, url, nav_type, is_main_frame ):
            if url.scheme() in ( "http", "https", "mailto" ):
                QtGui.QDesktopServices.openUrl( url )
                return False
            return super( _ManualPage, self ).acceptNavigationRequest( url, nav_type, is_main_frame )

    try:
        view = QtWebEngineWidgets.QWebEngineView( parent )
        view.setPage( _ManualPage( view ) )
    except Exception:
        return None
    return view


def start_component_mode():
    cmds.setToolTo( "selectSuperContext" )
    skin_cluster = _skin_cluster_name()
    if cmds.objExists( skin_cluster ):
        geometry = cmds.skinCluster( skin_cluster, q=True, g=True ) or []
        if geometry and cmds.objExists( geometry[0] ):
            cmds.select( geometry[0], r=True )
    mel.eval( "changeSelectMode -component" )


class SkinningToolsWindow( QtWidgets.QWidget ):

    def __init__( self, parent=None ):
        super( SkinningToolsWindow, self ).__init__( parent )
        self.setObjectName( _MAIN_WIN )
        self.setWindowFlags( QtCore.Qt.WindowType.Window )
        self.setAttribute( QtCore.Qt.WidgetAttribute.WA_DeleteOnClose )
        self.setWindowTitle( "%s  ver%s" % (_TOOL_NAME, _VERSION) )
        self.setStyleSheet( _TOOLTIP_STYLE )
        self.updating = False
        self.script_jobs = []
        self.freed = {"psw": 0, "sw": 0}

        layout = QtWidgets.QVBoxLayout( self )
        layout.setContentsMargins( 1, 0, 2, 3 )
        layout.setSpacing( 3 )
        layout.setMenuBar( self._build_menus() )

        self.splitter = _Splitter( QtCore.Qt.Orientation.Vertical )
        self.splitter.setHandleWidth( _SPLITTER_GAP * 2 )
        self.splitter.setChildrenCollapsible( False )
        self.psw_frame = self._build_paint_weights()
        self.sw_frame = self._build_set_weights()
        self.splitter.addWidget( self.psw_frame )
        self.splitter.addWidget( self.sw_frame )
        self.frames = {"psw": self.psw_frame, "sw": self.sw_frame}
        self.psw_frame.toggled.connect( lambda c: self._frame_toggled( "psw", c ) )
        self.sw_frame.toggled.connect( lambda c: self._frame_toggled( "sw", c ) )
        layout.addWidget( self.splitter, 1 )

        close_btn = QtWidgets.QPushButton( _tr( "Close" ) )
        close_btn.setFixedHeight( 30 )
        close_btn.setToolTip( _tr( "Close SkinningTools Window" ) )
        close_btn.clicked.connect( lambda *_: self.close() )
        layout.addWidget( close_btn )

        self.resize( *_WIN_SIZE )
        self.splitter.setSizes( [_PANE_TOP_PCT * 10, ( 100 - _PANE_TOP_PCT ) * 10] )

    def _build_menus( self ):
        bar = QtWidgets.QMenuBar( self )

        def add( menu, label, func, tip="" ):
            action = menu.addAction( _tr( label ) )
            action.triggered.connect( lambda *_: func() )
            if tip:
                action.setToolTip( _tr( tip ) )
            return action

        edit = bar.addMenu( _tr( "Edit" ) )
        self.auto_load_action = add( edit, "Auto Load Object", script_job_load )
        self.auto_load_action.setCheckable( True )
        self.auto_load_action.setChecked( True )
        add( edit, "Load Selected Object", load_selection )

        self.list_menu = bar.addMenu( _tr( "List" ) )
        order_group = QActionGroup( self )
        self.order_actions = {}
        for label in ( "Alphabetical", "Reverse Alphabetical", None, "Graph Order", "Reverse Graph Order",
                       None, "Hold", "Reverse Hold" ):
            if label is None:
                self.list_menu.addSeparator()
                continue
            action = add( self.list_menu, label, _order_changed )
            action.setCheckable( True )
            action.setChecked( label == "Alphabetical" )
            order_group.addAction( action )
            self.order_actions[label] = action

        tools = bar.addMenu( _tr( "Tools" ) )
        tools.setTearOffEnabled( True )
        add( tools, "Select Affected Points", lambda: select_affected_points( _skin_cluster_name() ) )
        add( tools, "Remove Unused Influences", remove_unused_influences )
        tools.addSeparator()
        add_remove = tools.addMenu( _tr( "Add/Remove Influences" ) )
        add( add_remove, "Add Influences", add_influences )
        add( add_remove, "Remove Influences", remove_influence )

        lang_menu = bar.addMenu( _tr( "Language" ) )
        lang_group = QActionGroup( self )
        for code, label in _LANGS:
            action = lang_menu.addAction( label )
            action.setCheckable( True )
            action.setChecked( code == _lang[0] )
            action.triggered.connect( lambda *_, _c=code: _switch_language( _c ) )
            lang_group.addAction( action )

        help_menu = bar.addMenu( _tr( "Help" ) )
        for label, file_name in _MANUALS:
            manual = help_menu.addAction( _tr( label ) )
            manual.triggered.connect( lambda *_, _l=label, _f=file_name: self._show_manual( _l, _f ) )
        update = help_menu.addAction( _tr( "Update" ) )
        update.triggered.connect( lambda *_: self._show_update() )
        about = help_menu.addAction( _tr( "About  {}" ).format( _TOOL_NAME ) )
        about.triggered.connect( lambda *_: self._show_about() )
        return bar

    def _show_manual( self, label, file_name ):
        path = _manual_path( file_name )
        if not os.path.isfile( path ):
            cmds.warning( _tr( "Manual not found: {}" ).format( path ) )
            return
        win_name = "%s_%s" % (_MANUAL_WIN, os.path.splitext( file_name )[0])
        for child in self.findChildren( QtWidgets.QDialog, win_name ):
            if child.isVisible():
                child.raise_()
                child.activateWindow()
                return
        dialog = QtWidgets.QDialog( self )
        dialog.setObjectName( win_name )
        dialog.setAttribute( QtCore.Qt.WidgetAttribute.WA_DeleteOnClose )
        dialog.setWindowTitle( "%s  -  %s" % (_TOOL_NAME, _tr( label )) )
        dialog.resize( 900, 800 )
        layout = QtWidgets.QVBoxLayout( dialog )
        layout.setContentsMargins( 0, 0, 0, 0 )
        url = QtCore.QUrl.fromLocalFile( path )
        view = _manual_web_view( dialog )
        if view is not None:
            view.setUrl( url )
        else:
            view = QtWidgets.QTextBrowser( dialog )
            view.setOpenExternalLinks( True )
            view.setSource( url )
        layout.addWidget( view )
        dialog.show()

    def _show_about( self ):
        dialog = QtWidgets.QDialog( self )
        dialog.setAttribute( QtCore.Qt.WidgetAttribute.WA_DeleteOnClose )
        dialog.setWindowTitle( _tr( "About  {}" ).format( _TOOL_NAME ) )
        dialog.setWindowModality( QtCore.Qt.WindowModality.ApplicationModal )
        layout = QtWidgets.QVBoxLayout( dialog )
        layout.setContentsMargins( 24, 18, 24, 14 )
        layout.setSpacing( 14 )
        title = QtWidgets.QLabel( "<b>%s&nbsp;&nbsp;&nbsp;ver%s</b>" % (_TOOL_NAME, _VERSION) )
        author = QtWidgets.QLabel( '<a href="%s">created by&nbsp;&nbsp;%s</a>' % (_AUTHOR_URL, _AUTHOR) )
        author.setTextInteractionFlags( QtCore.Qt.TextInteractionFlag.TextBrowserInteraction )
        author.setOpenExternalLinks( True )
        author.setToolTip( _AUTHOR_URL )
        ok_btn = QtWidgets.QPushButton( "OK" )
        ok_btn.setFixedWidth( 80 )
        ok_btn.setToolTip( _tr( "Close this dialog." ) )
        ok_btn.clicked.connect( dialog.close )
        layout.addWidget( title )
        layout.addWidget( author )
        layout.addWidget( ok_btn, 0, QtCore.Qt.AlignmentFlag.AlignRight )
        dialog.show()

    def _show_update( self ):
        dialog = QtWidgets.QDialog( self )
        dialog.setAttribute( QtCore.Qt.WidgetAttribute.WA_DeleteOnClose )
        dialog.setWindowTitle( _tr( "Update" ) )
        dialog.setWindowModality( QtCore.Qt.WindowModality.ApplicationModal )
        layout = QtWidgets.QVBoxLayout( dialog )
        layout.setContentsMargins( 24, 18, 24, 14 )
        layout.setSpacing( 14 )
        message = QtWidgets.QLabel( _tr( "The latest version is available here:" ) )
        link = QtWidgets.QLabel( '<a href="%s">%s</a>' % (_UPDATE_URL, _UPDATE_URL) )
        link.setTextInteractionFlags( QtCore.Qt.TextInteractionFlag.TextBrowserInteraction )
        link.linkActivated.connect(
            lambda url: ( QtGui.QDesktopServices.openUrl( QtCore.QUrl( url ) ), dialog.close() ))
        link.setToolTip( _UPDATE_URL )
        ok_btn = QtWidgets.QPushButton( "OK" )
        ok_btn.setFixedWidth( 80 )
        ok_btn.setToolTip( _tr( "Close this dialog." ) )
        ok_btn.clicked.connect( dialog.close )
        layout.addWidget( message )
        layout.addWidget( link )
        layout.addWidget( ok_btn, 0, QtCore.Qt.AlignmentFlag.AlignRight )
        dialog.show()

    def list_order( self ):
        for label, action in self.order_actions.items():
            if action.isChecked():
                return label
        return "Graph Order"

    def save_state( self ):
        sizes = self.splitter.sizes()
        for index, key in enumerate( ( "psw", "sw" ) ):
            sizes[index] += self.freed[key]
        return {"geometry": self.saveGeometry(),
                "extra_h": self.freed["psw"] + self.freed["sw"],
                "sizes": sizes,
                "order": self.list_order(),
                "auto_load": self.auto_load_action.isChecked(),
                "selected": _inf_selected()}

    def restore_state( self, state ):
        self.restoreGeometry( state["geometry"] )
        if state["extra_h"]:
            self.resize( self.width(), self.height() + state["extra_h"] )
        self.splitter.setSizes( state["sizes"] )
        self.auto_load_action.setChecked( state["auto_load"] )
        self.order_actions[state["order"]].setChecked( True )
        if state["order"] != "Alphabetical":
            _order_changed()
        if state["selected"]:
            _select_list_items( state["selected"] )
            paint_weights_function( "paint" )

    def _build_paint_weights( self ):
        frame = _CollapsibleFrame( _tr( "Paint Skin Weights" ) )
        body = frame.body_layout

        start_btn = _color_button( _tr( "Start Paint Mode" ), (0.4, 0.4, 0.45), h=27,
                                   tip=_tr( "Enter the Paint Skin Weights tool." ) )
        end_btn = _color_button( _tr( "End Paint Mode" ), (0.35, 0.35, 0.4), h=27,
                                 tip=_tr( "Exit the Paint Skin Weights tool." ) )
        start_btn.clicked.connect( lambda *_: enter_paint_mode() )
        end_btn.clicked.connect( lambda *_: cmds.setToolTo( "selectSuperContext" ) )
        body.addLayout( self._pair( start_btn, end_btn ) )

        row = QtWidgets.QHBoxLayout()
        row.setSpacing( 2 )
        self.hold_all_btn = QtWidgets.QPushButton( QtGui.QIcon( _lock_pixmap( True ) ), _tr( "Lock All" ) )
        self.unhold_all_btn = QtWidgets.QPushButton( QtGui.QIcon( _lock_pixmap( False ) ), _tr( "Unlock All" ) )
        for btn in ( self.hold_all_btn, self.unhold_all_btn ):
            btn.setIconSize( QtCore.QSize( 16, 16 ) )
        self.hold_all_btn.setToolTip( _tr( "Lock the weights of all influences." ) )
        self.unhold_all_btn.setToolTip( _tr( "Unlock the weights of all influences." ) )
        self.hold_all_btn.clicked.connect( lambda *_: hold_all_influences( 1 ) )
        self.unhold_all_btn.clicked.connect( lambda *_: hold_all_influences( 0 ) )
        self.sc_label = QtWidgets.QLabel( _tr( "Skin Cluster:" ) )
        self.sc_field = QtWidgets.QLineEdit()
        self.sc_field.setToolTip( _tr( "Skin cluster name. Right-click to select the skin cluster node or its geometry." ) )
        self.sc_field.editingFinished.connect( self._sc_field_changed )
        self.sc_field.setContextMenuPolicy( QtCore.Qt.ContextMenuPolicy.CustomContextMenu )
        self.sc_field.customContextMenuRequested.connect( self._sc_field_menu )
        self._sc_last = ""
        row.addWidget( self.hold_all_btn )
        row.addWidget( self.unhold_all_btn )
        row.addSpacing( 6 )
        row.addWidget( self.sc_label )
        row.addWidget( self.sc_field, 1 )
        body.addLayout( row )

        self.tree = _InfluenceTree()
        self.tree.setMinimumHeight( 40 )
        self.tree.lock_pressed.connect( _lock_button_pressed )
        self.tree.lock_dragged.connect( _lock_button_dragged )
        self.tree.lock_drag_finished.connect( _lock_drag_finished )
        self.tree.itemSelectionChanged.connect( _tree_selection_changed )
        self.tree.itemDoubleClicked.connect( _tree_item_double_clicked )
        self.tree.customContextMenuRequested.connect( self._tree_menu )
        body.addWidget( self.tree, 1 )

        lower = QtWidgets.QFrame()
        lower.setObjectName( "ST_PSWLower" )
        lower.setStyleSheet( "QFrame#ST_PSWLower { background-color: %s; }" % _rgb( _PSW_LOWER_BG_COLOR ) )
        grid = QtWidgets.QGridLayout( lower )
        pad = _PSW_LOWER_PAD
        grid.setContentsMargins( pad, pad, pad, pad )
        grid.setHorizontalSpacing( 5 )
        grid.setVerticalSpacing( 2 )

        top = QtWidgets.QHBoxLayout()
        top.setSpacing( 4 )
        brush_group = QtWidgets.QButtonGroup( self )
        brush_group.setExclusive( True )
        for i, ( name, icon, text ) in enumerate( _BRUSHES ):
            btn = QtWidgets.QToolButton()
            btn.setCheckable( True )
            btn.setFixedSize( 30, 30 )
            pix = QtGui.QPixmap( icon )
            if pix.isNull():
                btn.setText( text )
            else:
                btn.setIcon( QtGui.QIcon( pix ) )
                btn.setIconSize( QtCore.QSize( 26, 26 ) )
            btn.setChecked( i == 0 )
            btn.setToolTip( _tr( _BRUSH_TIPS[name] ) )
            btn.clicked.connect( lambda *_, _n=name: paint_weights_function( _n ) )
            brush_group.addButton( btn )
            top.addWidget( btn )
        top.addSpacing( 6 )
        ops = QtWidgets.QGridLayout()
        ops.setHorizontalSpacing( 8 )
        ops.setVerticalSpacing( 0 )
        self.op_group = QtWidgets.QButtonGroup( self )
        self.op_buttons = {}
        for i, ( name, _ ) in enumerate( _OPERATIONS ):
            rb = QtWidgets.QRadioButton( _tr( name ) )
            rb.setToolTip( _tr( _OPERATION_TIPS[name] ) )
            self.op_group.addButton( rb )
            self.op_buttons[name] = rb
            ops.addWidget( rb, i // 2, i % 2 )
        paint_mode = cmds.optionVar( q="ST_PaintMode" ) if cmds.optionVar( ex="ST_PaintMode" ) else "Add"
        self.set_operation( paint_mode if paint_mode in self.op_buttons else "Add" )
        for name, rb in self.op_buttons.items():
            rb.toggled.connect( lambda on, _n=name: on and paint_weights_function( _n.lower() ) )
        top.addLayout( ops )
        top.addStretch( 1 )
        color_btn = _color_button( _tr( "Color or Mono" ), (0.42, 0.42, 0.42), w=88,
                                   tip=_tr( "Switch the weight display in paint mode between color and grayscale." ) )
        color_btn.clicked.connect( lambda *_: color_or_mono() )
        top.addWidget( color_btn, 0, QtCore.Qt.AlignmentFlag.AlignVCenter )
        grid.addLayout( top, 0, 0, 1, 2 )

        opac_v = cmds.optionVar( q="ST_PSW_Opacity" ) if cmds.optionVar( ex="ST_PSW_Opacity" ) else 0
        val_v = cmds.optionVar( q="ST_PSW_Value" ) if cmds.optionVar( ex="ST_PSW_Value" ) else 0
        metrics = self.fontMetrics()
        label_w = max( [42] + [metrics.horizontalAdvance( _tr( t ) ) + 6 for t in ( "Opac", "Val" )] )
        self.opac = _FloatSliderGrp( _tr( "Opac" ), opac_v, 0, 1, 0, 1, 2, label_w=label_w )
        self.val = _FloatSliderGrp( _tr( "Val" ), val_v, 0, 1, -1.0, 2.0, 2, label_w=label_w )
        self.opac.changed.connect( lambda *_: paint_weights_function( "OpacityChange" ) )
        self.val.changed.connect( lambda *_: paint_weights_function( "ValueChange" ) )
        grid.addWidget( self.opac, 1, 0 )
        grid.addWidget( self.val, 2, 0 )

        flood_btn = QtWidgets.QPushButton( _tr( "Flood" ) )
        flood_btn.setFixedSize( max( 56, metrics.horizontalAdvance( flood_btn.text() ) + 16 ), 40 )
        flood_btn.setToolTip( _tr( "Flood the whole geometry with the current settings (Opac, Val) "
                                   "for the selected influence." ) )
        flood_btn.clicked.connect( lambda *_: paint_weights_function( "flood" ) )
        grid.addWidget( flood_btn, 1, 1, 2, 1,
                        QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter )
        grid.setColumnMinimumWidth( 1, flood_btn.width() + 8 )

        presets, flow = _flow_widget( 3 )
        _add_preset_label( flow, _tr( "Preset : " ) )
        prev_m = None
        for lbl, m, v, color, w in _PAINT_PRESETS:
            if m != prev_m:
                _add_preset_label( flow, _tr( "add" if m == "add" else "scale" ),
                                   gap=0 if prev_m is None else 8 )
            tip = ( "Set the paint operation to Add and Val to {}." if m == "add"
                    else "Set the paint operation to Scale and Val to {}." )
            btn = _color_button( lbl, color, w=w, tip=_tr( tip ).format( "%.2f" % v ) )
            btn.clicked.connect( lambda *_, _m=m, _v=v: set_val( _m, _v ) )
            flow.addWidget( btn )
            prev_m = m
        grid.addWidget( presets, 3, 0, 1, 2 )
        grid.setRowMinimumHeight( 3, 24 )

        body.addWidget( lower )
        return frame

    def _pair( self, left, right ):
        row = QtWidgets.QHBoxLayout()
        row.setSpacing( 0 )
        row.addWidget( left, 1 )
        row.addWidget( right, 1 )
        return row

    def current_operation( self ):
        for name, rb in self.op_buttons.items():
            if rb.isChecked():
                return name
        return ""

    def set_operation( self, name ):
        rb = self.op_buttons[name]
        rb.blockSignals( True )
        rb.setChecked( True )
        rb.blockSignals( False )

    def _sc_field_changed( self ):
        text = self.sc_field.text()
        if text == self._sc_last:
            return
        self._sc_last = text
        list_smooth_skin_influences( text, _active_set() )

    def _sc_field_menu( self, pos ):
        menu = QtWidgets.QMenu( self.sc_field )
        select_node = menu.addAction( _tr( "Select Skin Cluster Node" ) )
        select_geo = menu.addAction( _tr( "Select Geometry" ) )
        select_node.triggered.connect( lambda *_: cmds.select( self.sc_field.text(), r=True ) )
        select_geo.triggered.connect( lambda *_: cmds.select(
            cmds.skinCluster( self.sc_field.text(), q=True, g=True ) or [], r=True ) )
        menu.popup( self.sc_field.mapToGlobal( pos ) )

    def _tree_menu( self, pos ):
        menu = QtWidgets.QMenu( self.tree )
        update_popup( menu )
        menu.popup( self.tree.viewport().mapToGlobal( pos ) )

    def _build_set_weights( self ):
        frame = _CollapsibleFrame( _tr( "Set Vertex Weights:" ) )
        body = frame.body_layout

        start_btn = _color_button( _tr( "Start Component Mode" ), (0.4, 0.4, 0.45), h=27,
                                   tip=_tr( "Enter component mode." ) )
        end_btn = _color_button( _tr( "End Component Mode" ), (0.35, 0.35, 0.4), h=27,
                                 tip=_tr( "Return to object mode." ) )
        start_btn.clicked.connect( lambda *_: start_component_mode() )
        end_btn.clicked.connect( lambda *_: mel.eval( "changeSelectMode -object" ) )
        body.addLayout( self._pair( start_btn, end_btn ) )
        body.addSpacing( _SW_PRESET_GAP )

        presets, flow = _flow_widget( 2 )
        prev_v = None
        for lbl, v, color in _SW_PRESETS:
            if prev_v is None or ( prev_v > 0 ) != ( v > 0 ):
                _add_preset_label( flow, _tr( "Add:" if v > 0 else "Sub:" ), gap=0 if prev_v is None else 8,
                                   h=_SW_PRESET_H )
            prev_v = v
            if v > 0:
                tip = _tr( "Add {} to the weights of the selected influences on the selected vertices. "
                           "When cells of the table are selected, add it to the cells." )
            else:
                tip = _tr( "Subtract {} from the weights of the selected influences on the selected vertices. "
                           "When cells of the table are selected, subtract it from the cells." )
            btn = _color_button( lbl, color, w=_SW_PRESET_W + 6 if len( lbl ) > 5 else _SW_PRESET_W,
                                 h=_SW_PRESET_H, tip=tip.format( lbl[1:] ) )
            btn.clicked.connect( lambda *_, _v=v: set_weights( _v ) )
            flow.addWidget( btn )
        body.addWidget( presets )

        self.status_label = QtWidgets.QLabel()
        body.addWidget( self.status_label )

        self.table = _WeightTable()
        self.inf_header = _InfluenceHeader( self.table )
        self.table.setHorizontalHeader( self.inf_header )
        self.table.setItemDelegate( _WeightDelegate( self.table ) )
        self.table.setSelectionMode( QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection )
        self.table.setEditTriggers( QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
                                    | QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed )
        self.table.setMinimumHeight( _WT_MIN_HEIGHT )
        vtx_header = self.table.verticalHeader()
        vtx_header.setSectionResizeMode( QtWidgets.QHeaderView.ResizeMode.Fixed )
        vtx_header.setDefaultSectionSize( _WT_CELL_H )
        vtx_header.setMinimumWidth( 40 )
        vtx_header.setSectionsClickable( False )
        vtx_header.setHighlightSections( False )
        self.table.setCornerButtonEnabled( True )
        self.table.setStyleSheet(
            "QTableWidget { background-color: %s; gridline-color: rgb(55, 55, 55); "
            "selection-background-color: %s; selection-color: white; }"
            "QHeaderView { background-color: %s; border: none; }"
            "QTableCornerButton::section { background-color: %s; border: none; }"
            "QHeaderView::section:vertical { background-color: %s; color: rgb(220, 220, 220); "
            "border: none; border-bottom: 1px solid rgb(43, 43, 43); padding-right: 4px; }"
            % ( _rgb( _WT_BG_COLOR ), _rgb( _WT_CELL_SEL_COLOR ), _rgb( _WT_BG_COLOR ),
                _rgb( _WT_HEAD_BG_COLOR ), _rgb( _WT_VTX_COLOR ) ))
        self.inf_header.setStyleSheet( "QHeaderView { background-color: %s; border: none; }"
                                       % _rgb( _WT_HEAD_BG_COLOR ) )
        self.inf_header.lock_clicked.connect( _wt_lock_pressed )
        self.table.itemSelectionChanged.connect( _wt_update_status )
        self.table.selectionModel().selectionChanged.connect( _wt_track_cell_order )
        self.inf_header.name_clicked.connect( _wt_header_clicked )
        self.table.itemChanged.connect( _wt_item_changed )
        body.addWidget( self.table, 1 )

        copy_btn = _color_button( _tr( "Copy" ), (0.4, 0.4, 0.45), h=27,
                                  tip=_tr( "Copy the weights of the selected vertices, in the order they were "
                                           "selected. When cells of the table are selected, copy the cell values "
                                           "in the order they were selected." ) )
        self.paste_btn = _color_button( _paste_label(), (0.35, 0.35, 0.4), h=27,
                                        tip=_tr( "Paste the copied weights to the selected vertices, in the order "
                                                 "they were selected (if one vertex was copied, to all of them). "
                                                 "When cells of the table are selected, paste the copied cell values "
                                                 "to them in the same way. Locked influences are unlocked automatically." ) )
        copy_btn.clicked.connect( lambda *_: copy_weights() )
        self.paste_btn.clicked.connect( lambda *_: paste_weights() )
        body.addLayout( self._pair( copy_btn, self.paste_btn ) )
        return frame

    def _frame_toggled( self, key, collapsed ):
        frame = self.frames[key]
        index = 0 if key == "psw" else 1
        sizes = self.splitter.sizes()
        before = self.height()
        if collapsed:
            head = frame.header_height()
            target = before - max( sizes[index] - head, 0 )
            frame.setFixedHeight( head )
            sizes[index] = head
        else:
            frame.setMinimumHeight( 0 )
            frame.setMaximumHeight( 16777215 )
            target = before + self.freed[key]
            sizes[index] += self.freed[key]
            self.freed[key] = 0

        def finish():
            if collapsed:
                self.freed[key] = max( before - self.height(), 0 )
            self.splitter.setSizes( sizes )

        def resize_window():
            self.layout().invalidate()
            self.layout().activate()
            self.resize( self.width(), target )
            QtCore.QTimer.singleShot( 0, finish )

        QtCore.QTimer.singleShot( 0, resize_window )

    def start_script_jobs( self ):
        self.script_jobs = [
            cmds.scriptJob( event=["SelectionChanged", _on_selection_changed] ),
            cmds.scriptJob( event=["Undo", weight_table_refresh_values] ),
            cmds.scriptJob( event=["Redo", weight_table_refresh_values] ),
        ]

    def closeEvent( self, event ):
        for job in self.script_jobs:
            if job is not None and cmds.scriptJob( exists=job ):
                cmds.scriptJob( kill=job, force=True )
        self.script_jobs = []
        if _win[0] is self:
            _win[0] = None
        super( SkinningToolsWindow, self ).closeEvent( event )


def _tree_selection_changed():
    paint_weights_function( "paint" )
    _wt_sync_header_selection()


def _order_changed():
    list_smooth_skin_influences( _skin_cluster_name(), _active_set() )


def _switch_language( lang ):
    if lang == _lang[0]:
        return
    cmds.optionVar( sv=[_LANG_OPTVAR, lang] )
    ui = _ui()
    state = ui.save_state() if ui else None
    QtCore.QTimer.singleShot( 0, lambda: _reopen( state ) )


def _reopen( state ):
    win = main()
    if state:
        win.restore_state( state )


def main():
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if widget.objectName() == _MAIN_WIN:
            widget.close()

    _load_lang()

    cmds.selectPref( trackSelectionOrder=True )

    win = SkinningToolsWindow( _maya_main_window() )
    _win[0] = win
    win.start_script_jobs()
    win.show()

    select_full_set()
    script_job_load()
    weight_table_refresh()
    return win


if __name__ == "__main__":
    main()
