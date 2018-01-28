port module Hpg exposing (..)

import Html exposing (..)
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


pickCharset : Bool -> Charset
pickCharset useSymbols =
  case useSymbols of
    True -> allPrintableChars
    False -> alphaChars


port generatePassword : PWOptions -> Cmd msg
port passwordGenerated : (String -> msg) -> Sub msg


{--
  UI Functions
--}

main : Program Never Model Msg
main =
  program
   { init = init
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


init : (Model, Cmd Msg)
init =
  let defaultOptions = (PWOptions "" "" allPrintableChars 14) in
   ( Model defaultOptions "" True, generatePassword defaultOptions )


type Msg =
   Identifier String
  | Salt String
  | UseSymbols Bool
  | Length String
  | PasswordGenerated String


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


view : Model -> Html Msg
view model =
  div [ id "main", class "col-lg-6" ]
    [ h2 [] [ text "HPG: Generate a password" ]
    , Html.form [ class "form-horizontal well" ]
      [ label [ for "inputIdentifier" ]
        [ text "Identifier" ]
      , input
        [ type_ "text"
        , id "inputIdentifier"
        , class "form-control"
        , placeholder "foo@foo.com"
        , value model.options.identifier
        , onInput Identifier] []
      , br [] []
      , label [ for "inputPassword" ]
        [ text "Master Password" ]
      , input
        [ type_ "password"
        , id "inputPassword"
        , class "form-control"
        , placeholder "my-secret-password"
        , value model.options.salt
        , onInput Salt] []
      , br [] []
      , label [ for "inputLength" ]
        [ text "Length" ]
      , input
        [ type_ "number"
        , id "inputLength"
        , class "form-control"
        , Att.min "1"
        , step "1"
        , value (toString model.options.length)
        , onInput Length
        ] []
      , br [] []
      , label []
        [ input
          [ type_ "checkbox"
          , checked model.useSymbols
          , onCheck UseSymbols] []
        , text " Use Symbols "
        ]
      ]
    , div [ id "generatedPassword", class "well" ]
      [ h3 []
        [ text "Password: "
        , text model.password
        ]
      ]
    ]
