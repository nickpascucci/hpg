port module Hpg exposing (..)

import Html exposing (..)
import Html.App as Html
import Html.Attributes as Att exposing (..)
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


pickCharset : Bool -> Charset
pickCharset useSymbols =
  case useSymbols of
    True -> allPrintableChars
    False -> alphaChars


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
  | Length String
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
            charset = pickCharset useSymbols}}
        in
         (newModel, generatePassword newModel.options)
      Length len ->
        case String.toInt len of
          Err msg -> (model, Cmd.none)
          Ok newLength ->
            let newModel = {model | options =
              { currentOptions | length = newLength}} in
                (newModel, generatePassword newModel.options)
      PasswordGenerated password ->
         ({model | password = password}, Cmd.none)


subscriptions : Model -> Sub Msg
subscriptions model =
  passwordGenerated PasswordGenerated


css : String -> Html Msg
css path =
  node "link" [ rel "stylesheet", href path ] []


view : Model -> Html Msg
view model =
  div [ id "main" ]
   [ css "hpg.css"
   , label []
      [ text "Identifier"
      , input
        [ type' "text"
        , placeholder "foo@foo.com"
        , value model.options.identifier
        , onInput Identifier] []
      ]
   , br [] []
   , label []
      [ text "Master Password"
      , input
        [ type' "password"
        , placeholder "my-secret-password"
        , value model.options.salt
        , onInput Salt] []
      ]
   , br [] []
   , label []
      [ text "Length"
      , input
        [ type' "number"
        , Att.min "1"
        , step "1"
        , value (toString model.options.length)
        , onInput Length
        ] []
      ]
   , br [] []
   , label []
      [ text "Use Symbols"
      , input
        [ type' "checkbox"
        , checked model.useSymbols
        , onCheck UseSymbols] []
      ]
   , div []
      [ text model.password ]
   ]
