
from p8.prompt.prompt import PARAM_COLLECTOR_PROMPT
from p8.llm.n1n import N1N_LLM
from p8.llm.message import Message
from p8.tools.utils import extract_and_validate_json, \
    get_table_context, \
        parse_response,\
            execute_task,extract_top_genes


class ParamCollectorNode:
    def __init__(self, LLM, marker_table = None) -> None:
        self.llm = LLM
        self.marker_table = marker_table
    
    def prep(self):
        self.table_summary = get_table_context(self.marker_table)
    
    def run(self):
        message_input = Message(system_prompt=PARAM_COLLECTOR_PROMPT)
        message_input.add_user_message(self.table_summary)

        while True:
            response = self.llm.invoke_stream(message_input)

            final_params = extract_and_validate_json(response)
            
            if final_params:
                break

            message_input.add_ai_message(response)

            user_input = input("\n\n[You]:\n\n")
            message_input.add_user_message(user_input)
        

        results = parse_response(final_params)
        results.update({'df': self.marker_table})

        res = execute_task(
            extract_top_genes, results
        )
        return res

def main():

    llm = N1N_LLM(
        api_key = 'sk-VW019xQdJlI0EJKpESIj8UcUYWTMyBop78hsJQ2W5P8ppe3D',
        model_name = 'gemini-3.1-pro-preview',
        base_url = "https://api.n1n.ai/v1"
    )

    pcnode = ParamCollectorNode(llm, "/home/zhliu/test/p8/deg_sig_fc_up_padj(2).csv")
    pcnode.prep()
    a = pcnode.run()

    print(a)

if __name__ == '__main__':
    main()

