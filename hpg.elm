port module Hpg exposing (..)

import Html exposing (..)
import Html.App as Html
import Html.Attributes exposing (..)
import Html.Events exposing (onClick, onInput, onCheck)
import String

type alias Identifier = String
type alias Salt = String
type alias Charset = String


alphaChars : Charset
alphaChars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


symbolChars : Charset
symbolChars = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~';"


allPrintableChars : Charset
allPrintableChars = alphaChars ++ symbolChars


generate : Salt -> Identifier -> Charset -> Int -> String
generate salt identifier charset length =
   filterToCharset charset (identifier ++ salt)


filterToCharset : Charset -> String -> String
filterToCharset charset str =
  String.filter (\c -> String.contains (String.fromChar c) charset) str

{--
  UI Functions
--}

main : Program Never
main =
  Html.program
   { init = defaultModel
   , view = view
   , update = update
   , subscriptions = subscriptions}


type alias PWOptions =
  { salt : Salt
  , identifier : Identifier
  , charset : Charset
  , length : Int
  }


type alias Model =
  { options : PWOptions
  , password : String
  , useSymbols : Bool
  }


defaultModel : (Model, Cmd Msg)
defaultModel =
   (Model (PWOptions "" "" allPrintableChars 14) "" True,
    Cmd.none)


type Msg =
   Identifier String
  | Salt String
  | UseSymbols Bool
  | PasswordGenerated String


port generatePassword : PWOptions -> Cmd msg
port passwordGenerated : (String -> msg) -> Sub msg


update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
  let currentOptions = model.options in
    case msg of
      Identifier identifier ->
        let newModel = {model | options =
           { currentOptions | identifier = identifier}} in
            (newModel, generatePassword newModel.options)
      Salt salt ->
        let newModel = {model | options = { currentOptions | salt = salt}} in
           (newModel, generatePassword newModel.options)
      UseSymbols useSymbols ->
        let newModel = {model |
          useSymbols = useSymbols,
          options = { currentOptions |
            charset = if useSymbols then allPrintableChars else alphaChars}}
        in
         (newModel, generatePassword newModel.options)
      PasswordGenerated password ->
         ({model | password = password}, Cmd.none)


subscriptions : Model -> Sub Msg
subscriptions model =
  passwordGenerated PasswordGenerated

charset : Bool -> Charset
charset useSymbols =
  case useSymbols of
    True -> allPrintableChars
    False -> alphaChars


css : String -> Html Msg
css path =
  node "link" [ rel "stylesheet", href path ] []


view : Model -> Html Msg
view model =
  div [ id "main" ]
   [ css "hpg.css"
   , label []
      [ input
        [type' "text"
        , placeholder "Identifier"
        , value model.options.identifier
        , onInput Identifier] []
      , text "Identifier"
      ]
   , label []
      [ input
        [type' "password"
        , placeholder "Salt"
        , value model.options.salt
        , onInput Salt] []
      , text "Salt"
      ]
   , label []
      [ input
        [type' "checkbox"
        , checked model.useSymbols
        , onCheck UseSymbols] []
      , text "Use Symbols"
      ]
   , div []
      [ text model.password ]
   ]
